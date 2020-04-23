import os
import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

_greeter = "http://localhost:9082" if (os.environ.get("GREETER") is None) else os.environ.get("GREETER")
_port    = 9081 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/')
def pub():
    hello_to = request.args.get('helloTo')
    g_message = greeter(_greeter, 'helloTo', hello_to)
    publisher('publisher: {}'.format(g_message))
    return g_message

def greeter(url, param, value):
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text

def publisher(message):
    print(message, flush=True)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
