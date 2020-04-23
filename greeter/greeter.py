import os
import requests
from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

_port = 9082 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg  = "Http Hello" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")

app = Flask(__name__)
metrics = PrometheusMetrics(app)

@app.route('/')
def greeter():
    hello_to = request.args.get('helloTo')
    return '%s, %s!' % (_msg, hello_to)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
