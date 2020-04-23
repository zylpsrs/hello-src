import os
import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

_publisher = "http://localhost:9081" if (os.environ.get("PUBLISHER") is None) else os.environ.get("PUBLISHER")
_greeter   = "http://localhost:9082" if (os.environ.get("GREETER") is None) else os.environ.get("GREETER")
_port      = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/')
def hello():
    hello_to = request.args.get('helloTo')
    p_messages=publisher(_publisher, 'helloTo', hello_to)
    g_messages=greeter(_greeter, 'helloTo', hello_to)
    return "publisher: {}\ngreeter  : {}\n".format(p_messages,g_messages)

def publisher(url, param, value):
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text

def greeter(url, param, value):
    r = requests.get(url, params={param: value})
    assert r.status_code == 200
    return r.text

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
