import os
import requests
from flask import Flask, request

_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)

@app.route('/')
def hello():
    hello_to = request.args.get('helloTo')
    printer(formater(hello_to))

def formater(hello_to):
    return "Hello, {}".format(hello_to)

def printer(messages):
    print(messages, flush=True)
    return messages

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
