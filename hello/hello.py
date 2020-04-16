import os
import sys
import requests

from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics

from lib.tracing import init_tracer,http_trace,local_trace,http_debug
from lib.tracing import get_forward_http_headers
from opentracing_instrumentation.request_context import get_current_span, span_in_context

publisher_svc = "localhost:9081" if (os.environ.get("PUBLISHER_SERVICE") is None) else os.environ.get("PUBLISHER_SERVICE")
_port = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

tracer = init_tracer("hello")
app = Flask(__name__)
http_debug(app)
PrometheusMetrics(app)

@app.route('/')
@http_trace(tracer, "hello")
def hello():
    hello_to = request.args.get('helloTo')
    return publisher("http://{}".format(publisher_svc), 'helloTo', hello_to)

def publisher(url, param, value):
    headers=get_forward_http_headers(tracer)
    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=False, threaded=True)
