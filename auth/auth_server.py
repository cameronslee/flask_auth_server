### AUTH SERVER ###
import json
import time

import sqlite3
import click

import urllib.parse as urlparse

from urllib.parse import urlencode
from cryptography.fernet import Fernet

from flask import Flask, request, redirect, render_template, g, current_app, flash

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

# Setup DB
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

##################################################
KEY = Fernet.generate_key()
MAX_AUTH_CODE_LIFETIME = 600 # 10min (RFC6749 pg26)
##################################################

# TODO
def authenticate_client(client_id, client_secret):
  # Query DB, check that client_id and client_secret exists
  return True

# TODO: add verifcation for valid client, would be done upon registering an application
def verify_client(client_id, redirect_uri):
  return True

# TODO
def authenticate_user(username, password):
  # Query DB, check that username and password exists
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
    db.execute("INSERT INTO auth_codes(exp, client_id, redirect_uri) VALUES (?,?,?)",
    (expiration_date, client_id, redirect_uri)
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

def process_redirect_uri(redirect_url, authorization_code):
# Prepare the redirect URL
  url_parts = list(urlparse.urlparse(redirect_url))
  queries = dict(urlparse.parse_qsl(url_parts[4]))
  queries.update({ "authorization_code": authorization_code })
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

  if None in [ username, password, client_id, redirect_uri ]:
    print(username, password, client_id, redirect_uri)
    return json.dumps({
      "error": "invalid_request"
    }), 400

  if not authenticate_user(username, password):
    return json.dumps({
      'error': 'access_denied'
    }), 401

  authorization_code = generate_authorization_code(client_id, redirect_uri)

  uri = process_redirect_uri(redirect_uri, authorization_code)

  return redirect(uri, code = 303)

if __name__ == '__main__':
  app.run(port = 8001, debug = True)
