import os
import requests
from flask import Flask, request, session
from lib.tracing import init_jaeger_tracer, get_forward_http_headers
from lib.tracing import flask_top_request_trace, flask_child_method_trace

_port    = 9082 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg     = "Http Hello" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")
_service = os.path.basename(__file__).split('.')[0]
_debug   = False

app = Flask(__name__)
tracer = init_jaeger_tracer(_service)

@app.route('/')
@flask_top_request_trace(tracer, "greeter")
def greeter():
    hello_to = request.args.get('helloTo')
    return '%s, %s!' % (_msg, hello_to)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=_debug, threaded=True)
