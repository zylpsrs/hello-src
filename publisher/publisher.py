import os
import requests
from flask import Flask, request, session
from lib.tracing import init_jaeger_tracer, get_forward_http_headers
from lib.tracing import flask_top_request_trace, flask_child_method_trace

_greeter = "http://localhost:9082" if (os.environ.get("GREETER") is None) else os.environ.get("GREETER")
_port    = 9081 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_service = os.path.basename(__file__).split('.')[0]
_debug   = False

app = Flask(__name__)
tracer = init_jaeger_tracer(_service)

@app.route('/')
@flask_top_request_trace(tracer, "pub")
def pub():
    hello_to = request.args.get('helloTo')
    g_message = greeter(_greeter, 'helloTo', hello_to)
    publisher('publisher: {}'.format(g_message))
    return g_message

@flask_child_method_trace(tracer, "greeter")
def greeter(url, param, value):
    headers = get_forward_http_headers(tracer)
    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text

@flask_child_method_trace(tracer, "publisher")
def publisher(message):
    print(message, flush=True)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=_debug, threaded=True)