### CLIENT SERVER ###
import json
import requests
from flask import Flask, request, render_template, make_response, redirect, url_for

app = Flask(__name__)
AUTH_PATH = 'http://localhost:8001/auth'
TOKEN_PATH = 'http://localhost:8001/token'
RES_PATH = 'http://localhost:8002/data'
REDIRECT_URI = 'http://localhost:8000/callback'

CLIENT_ID = 'foo-client-id'
CLIENT_SECRET = 'foo-client-secret'
RESPONSE_TYPE = 'code'

@app.before_request
def before_request():
  if request.endpoint not in ['login', 'callback']:
    access_token = request.cookies.get('access_token')
    if access_token:
      pass
    else:
      return redirect(url_for('login'))

@app.route('/')
def main():
  access_token = request.cookies.get('access_token')

  r = requests.get(RES_PATH, headers = {
    'Authorization': 'Bearer {}'.format(access_token)
  })

  if r.status_code != 200:
    return json.dumps({
      'error': 'The resource server returns an error: \n{}'.format(
        r.text)
    }), 500

  data = json.loads(r.text).get('results')

  return render_template('data.html', data = data)

@app.route('/login')
def login():
  # TODO add state
  return render_template('login.html',
                         dest = AUTH_PATH,
                         client_id = CLIENT_ID,
                         response_type = RESPONSE_TYPE,
                         redirect_uri = REDIRECT_URI,
                         )

@app.route('/callback')
def callback():
  authorization_code = request.args.get('code')

  if not authorization_code:
    return json.dumps({
      'error': 'authorization code not present'
    }), 500

  r = requests.post(TOKEN_PATH, data = {
    "grant_type": "authorization_code",
    "authorization_code": authorization_code,
    "client_id" : CLIENT_ID,
    "client_secret" : CLIENT_SECRET,
    "redirect_url": REDIRECT_URI 
  })
  
  if r.status_code != 200:
    return json.dumps({
      'error': 'authorization server error: \n{}'.format(
        r.text)
    }), 500
  
  access_token = json.loads(r.text).get('access_token')
  response = make_response(redirect(url_for('main')))
  response.set_cookie('access_token', access_token)

  return response

if __name__ == '__main__':
  app.run(port = 8000, debug = True)
