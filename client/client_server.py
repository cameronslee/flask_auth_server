### CLIENT SERVER ###
import json
import requests
from flask import Flask, request, render_template

app = Flask(__name__)
AUTH_PATH = 'http://localhost:8001/auth'
TOKEN_PATH = 'http://localhost:8001/token'
RES_PATH = 'http://localhost:8002/users'
REDIRECT_URI = 'http://localhost:8000/callback'

CLIENT_ID = 'sample-client-id'
CLIENT_SECRET = 'sample-client-secret'
RESPONSE_TYPE = 'code'

@app.before_request
def before_request():
  pass

@app.route('/login')
def login():
  # Construct request URI
# TODO add state
  return render_template('login.html',
                         dest = AUTH_PATH,
                         client_id = CLIENT_ID,
                         response_type = RESPONSE_TYPE,
                         redirect_uri = REDIRECT_URI,
                         )

@app.route('/callback')
def callback():
  return 'TODO foo'


if __name__ == '__main__':
  app.run(port = 8000, debug = True)
