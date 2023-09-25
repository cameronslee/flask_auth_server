import json

from flask import Flask, request

app = Flask(__name__)

@app.before_request
def before_request():
  pass

if __name__ == '__main__':
  app.run(port = 8000, debug = True)
