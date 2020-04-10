import os
import requests
from flask import Flask, request

publisher_svc = "localhost:9081" if (os.environ.get("PUBLISHER_SERVICE") is None) else os.environ.get("PUBLISHER_SERVICE")
_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)

@app.route('/')
def hello():
    hello_to = request.args.get('helloTo')
    messages=publisher("http://{}".format(publisher_svc), 'helloTo', hello_to)
    return messages

def publisher(url, param, value):
    print("url")
    print("--------------------------------------------")
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
