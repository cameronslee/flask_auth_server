### AUTH SERVER ###
import json
import jwt
import time

import sqlite3
import click

import urllib.parse as urlparse

from urllib.parse import urlencode
from cryptography.fernet import Fernet

from flask import Flask, request, Response, redirect, render_template, g, flash

with open('private_key.pem', 'rb') as file:
  private_key = file.read()

app = Flask(__name__)

app.config.from_mapping(
  SECRET_KEY='DEV',
  )

def get_db():
  if 'db' not in g:
    g.db = sqlite3.connect(
      'auth.sqlite',
      detect_types=sqlite3.PARSE_DECLTYPES
    )
    g.db.row_factory = sqlite3.Row

  return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
      db.close()

def init_db():
  db = get_db()
  with app.open_resource('schema.sql') as f:
    db.executescript(f.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
  init_db()
  click.echo('Initialized DB')

# Register application
app.teardown_appcontext(close_db)
app.cli.add_command(init_db_command)

KEY = Fernet.generate_key()
ISSUER = 'foo-auth-server'
MAX_AUTH_CODE_LIFETIME = 600 # 10min (RFC6749 pg26)
JWT_LIFETIME = 1800

def authenticate_client(client_id, client_secret):
  db = get_db()
  record = db.execute('SELECT * FROM applications WHERE client_secret= ? AND client_id= ?', (client_secret,client_id)).fetchone()
  return False if not record else True

def verify_client(client_id, redirect_uri):
  db = get_db()
  record = db.execute('SELECT * FROM clients WHERE client_id= ? AND redirect_uri= ?', (client_id,redirect_uri)).fetchone()
  return False if not record else True

def authenticate_user(username, password):
  db = get_db()
  record = db.execute('SELECT * FROM users WHERE username= ? AND password= ?', (username,password)).fetchone()
  return False if not record else True

def generate_access_token():
  payload = {
    "iss": ISSUER,
    "exp": time.time() + JWT_LIFETIME
  }

  access_token = jwt.encode(payload, private_key, algorithm = 'RS256')

  return access_token

def verify_authorization_code(authorization_code, client_id, redirect_uri):
  db = get_db()
  authorization_code = authorization_code.encode()
  record = db.execute('SELECT * FROM auth_codes WHERE authorization_code= ?', (authorization_code,)).fetchone()

  if not record:
    return False

  record_exp = record['exp']
  record_client_id = record['client_id']
  record_redirect_uri = record['redirect_uri']

  if time.time() > record_exp or record_client_id != client_id or record_redirect_uri != redirect_uri:
    return False

  return True

def generate_authorization_code(client_id, redirect_uri):
  f = Fernet(KEY)
  authorization_code = f.encrypt(json.dumps({
    "client_id": client_id,
    "redirect_uri": redirect_uri,
  }).encode())

  error = None
  db = get_db()

  expiration_date = time.time() + MAX_AUTH_CODE_LIFETIME
 
  try:
    db.execute("INSERT INTO auth_codes(authorization_code, exp, client_id, redirect_uri) VALUES (?,?,?,?)",
    (authorization_code, expiration_date, client_id, redirect_uri)
    )
    db.commit()
  except db.IntegrityError:
    error = f"Auth Code already exists"
  flash(error)

  return authorization_code

@app.route('/auth')
def auth():
  client_id = request.args.get('client_id')
  redirect_uri = request.args.get('redirect_uri')

  if None in [client_id, redirect_uri]:
    return json.dumps({
      "error": "invalid request"
    }), 400

  if not verify_client(client_id, redirect_uri):
    return json.dumps({
      "error": "invalid client"
    }), 400 

  return render_template('grant_access.html',
                         client_id = client_id,
                         redirect_uri = redirect_uri)

def form_redirect_uri(redirect_url, authorization_code):
  url_parts = list(urlparse.urlparse(redirect_url))
  queries = dict(urlparse.parse_qsl(url_parts[4]))
  queries.update({ "code": authorization_code })
  url_parts[4] = urlencode(queries)
  url = urlparse.urlunparse(url_parts)
  return url

@app.route('/signin', methods = ['POST'])
def signin():
  # Issues authorization code
  username = request.form.get('username')
  password = request.form.get('password')
  client_id = request.form.get('client_id')
  redirect_uri = request.form.get('redirect_uri')
  
  # Error Response
  if None in [ username, password, client_id, redirect_uri ]:
    return json.dumps({
      "error": "invalid_request"
    }), 400

  if not verify_client(client_id, redirect_uri):
    return json.dumps({
      'error': 'unauthorized_client'
    }), 401

  if not authenticate_user(username, password):
    return json.dumps({
      'error': 'access_denied'
    }), 401

  response = Response()
  if response.status_code != 200:
    error_text = json.loads(request.text).get('error')
    print(error_text)
    if error_text == 'unsupported_response_type' or error_text == 'invalid_scope' or error_text == 'server_error':
      return json.dumps({
        'error': error_text 
      }), 500
    elif error_text == 'temporarily_unavailable':
      return json.dumps({
        'error': error_text
      }), 503

  authorization_code = generate_authorization_code(client_id, redirect_uri)

  uri = form_redirect_uri(redirect_uri, authorization_code)
  
  return redirect(uri, code = 302)

@app.route('/token', methods = ['POST'])
def exchange_for_token():
  authorization_code = request.form.get('authorization_code')
  client_id = request.form.get('client_id')
  client_secret = request.form.get('client_secret')
  redirect_url = request.form.get('redirect_url')

  if None in [ authorization_code, client_id, client_secret, redirect_url ]:
    return json.dumps({
      "error": "invalid_request"
    }), 400

  if not authenticate_client(client_id, client_secret):
    return json.dumps({
      "error": "invalid_client"
    }), 400

  if not verify_authorization_code(authorization_code, client_id, redirect_url):
    return json.dumps({
      "error": "access_denied"
    }), 400

  access_token = generate_access_token()
  
  return json.dumps({ 
    "access_token": access_token.decode(),
    "token_type": "JWT",
    "expires_in": JWT_LIFETIME
  })

if __name__ == '__main__':
  app.run(port = 8001, debug = True)
