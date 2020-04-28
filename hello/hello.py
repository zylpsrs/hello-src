import os
import requests
from flask import Flask, request, session
from lib.tracing import init_jaeger_tracer, get_forward_http_headers
from lib.tracing import flask_top_request_trace, flask_child_method_trace

_publisher = "http://localhost:9081" if (os.environ.get("PUBLISHER") is None) else os.environ.get("PUBLISHER")
_greeter   = "http://localhost:9082" if (os.environ.get("GREETER") is None) else os.environ.get("GREETER")
_port      = 9080 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_service   = os.path.basename(__file__).split('.')[0]
_debug     = False

app = Flask(__name__)
tracer = init_jaeger_tracer(_service)

@app.route('/')
@flask_top_request_trace(tracer, "hello")
def hello():
    hello_to = request.args.get('helloTo')
    p_messages=publisher(_publisher, 'helloTo', hello_to)
    g_messages=greeter(_greeter, 'helloTo', hello_to)
    return "publisher: {}\ngreeter  : {}\n".format(p_messages,g_messages)

@flask_child_method_trace(tracer, "publisher")
def publisher(url, param, value):
    headers = get_forward_http_headers(tracer)
    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text

@flask_child_method_trace(tracer, "greeter")
def greeter(url, param, value):
    headers = get_forward_http_headers(tracer)
    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=_debug, threaded=True)
