### RESOURCE SERVER ###
import json

from flask import Flask, request

app = Flask(__name__)

import jwt

ISSUER = 'foo-auth-server'

with open('public_key.pem', 'rb') as f:
  public_key = f.read()

def verify_access_token(access_token):
  try:
    decoded_token = jwt.decode(access_token, public_key,
                               issuer = ISSUER,
                               algorithm = 'RS256')
  except (jwt.exceptions.InvalidTokenError,
          jwt.exceptions.InvalidSignatureError,
          jwt.exceptions.InvalidIssuerError,
          jwt.exceptions.ExpiredSignatureError) as e:
    print(e)
    return False

  return True

@app.before_request
def before_request():
  auth_header = request.headers.get('Authorization')
  if 'Bearer' not in auth_header:
    return json.dumps({
      'error': 'Access token not present'
    }), 400
  
  access_token = auth_header[7:]

  if not access_token or not verify_access_token(access_token):
    print(access_token)
    return json.dumps({
      'error': 'Access token invalid.'
    }), 400

@app.route('/data', methods = ['GET'])
def get_user():
  data = [
    { 'content': 'foo'},
    { 'content': 'bar'},
    { 'content': 'barfoo'},
    { 'content': 'foobar'},
  ]

  return json.dumps({
    'results': data
  })

if __name__ == '__main__':
  app.run(port = 8002, debug = True)