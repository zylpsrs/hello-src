import os
import requests
from flask import Flask, request

_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg  = "Hello" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")

app = Flask(__name__)

@app.route('/')
def hello():
    hello_to = request.args.get('helloTo')
    messages=greeter(hello_to)
    publisher(messages)
    return messages

def greeter(hello_to):
    return "{}, {}".format(_msg,hello_to)

def publisher(messages):
    print(messages, flush=True)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
