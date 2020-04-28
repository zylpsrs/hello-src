import os
import requests
from flask import Flask, request, session
from lib.tracing import init_jaeger_tracer, get_forward_http_headers
from lib.tracing import flask_top_request_trace, flask_child_method_trace
from lib.tracing import active_span_source_usage_by_grpc

import grpc
from lib import greeter_pb2
from lib import greeter_pb2_grpc
from grpc_opentracing.grpcext import intercept_channel
from grpc_opentracing import open_tracing_client_interceptor

_publisher = "http://localhost:9081" if (os.environ.get("PUBLISHER") is None) else os.environ.get("PUBLISHER")
_greeter   = "localhost:9082" if (os.environ.get("GREETER") is None) else os.environ.get("GREETER")
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
    g_messages=greeter(_greeter, hello_to)
    return "publisher: {}\ngreeter  : {}\n".format(p_messages,g_messages)

@flask_child_method_trace(tracer, "publisher")
def publisher(url, param, value):
    headers = get_forward_http_headers(tracer)
    r = requests.get(url, params={param: value}, headers=headers)
    assert r.status_code == 200
    return r.text

@flask_child_method_trace(tracer, "greeter")
def greeter(_greeter, hello_to):
    interceptor = open_tracing_client_interceptor(tracer,
                    active_span_source=active_span_source_usage_by_grpc)
    with grpc.insecure_channel(_greeter) as channel:
        channel = intercept_channel(channel, interceptor)
        stub = greeter_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greeter_pb2.HelloRequest(name=hello_to))
    return response.message

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=_debug, threaded=True)
