import os
import requests
from flask import Flask, request

greeter_svc = "localhost:9082" if (os.environ.get("GREETER_SERVICE") is None) else os.environ.get("GREETER_SERVICE")
_port = 9081 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)

@app.route('/')
def pub():
    hello_to = request.args.get('helloTo')
    publisher('publisher!')
    return greete("http://{}".format(greeter_svc), 'helloTo', hello_to)

def greete(url, param, value):
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text

def publisher(messages):
    print(messages, flush=True)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
