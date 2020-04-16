import os
import sys
import requests

from flask import Flask, request
from prometheus_flask_exporter import PrometheusMetrics
from lib.tracing import init_tracer,http_trace,local_trace,http_debug

import grpc
from lib import greeter_pb2
from lib import greeter_pb2_grpc

from grpc_opentracing import open_tracing_client_interceptor, ActiveSpanSource
from grpc_opentracing.grpcext import intercept_channel

greeter_svc = "localhost:9082" if (os.environ.get("GREETER_SERVICE") is None) else os.environ.get("GREETER_SERVICE")
_port = 9081 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

app = Flask(__name__)
http_debug(app)
PrometheusMetrics(app)
tracer = init_tracer("publisher")

@app.route('/')
@http_trace(tracer, "pub")
def pub():
    hello_to = request.args.get('helloTo')
    message=hello(hello_to)
    publisher(message)
    return message

def hello(hello_to):
    interceptor = open_tracing_client_interceptor(tracer)
    with grpc.insecure_channel(greeter_svc) as channel:
        channel = intercept_channel(channel, interceptor)
        stub = greeter_pb2_grpc.GreeterStub(channel)
        response = stub.SayHello(greeter_pb2.HelloRequest(name=hello_to))
    return response.message

@http_trace(tracer, "publisher")
def publisher(messages):
    print(messages, flush=True)

if __name__ == "__main__":
    app.run(host='::', port=_port, debug=False, threaded=True)
