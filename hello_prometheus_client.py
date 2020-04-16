import os
from flask import Flask, Response

import prometheus_client
from prometheus_client.core import CollectorRegistry

_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg  = "Hello, World!" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")

REGISTRY = CollectorRegistry(auto_describe=False)
flask_http_request_total = prometheus_client.Counter(
    "flask_http_request_total","flask http request total", 
    ['method', 'endpoint'], registry=REGISTRY)
flask_http_request_duration_seconds = prometheus_client.Histogram(
    "flask_http_request_duration_seconds",
    "flask http request duration seconds", registry=REGISTRY)

app = Flask(__name__)

@app.route('/')
@flask_http_request_duration_seconds.time()
def hello():
    flask_http_request_total.labels(method='get', endpoint='/').inc()
    return "{}".format(_msg)

@app.route("/metrics")
def requests_count():
    return Response(prometheus_client.generate_latest(REGISTRY),
                    mimetype="text/plain")

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=True, threaded=True)
