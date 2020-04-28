from concurrent import futures
import os
import logging
from time import sleep
from lib.tracing import init_jaeger_tracer

import grpc
from lib import greeter_pb2
from lib import greeter_pb2_grpc
from grpc_opentracing.grpcext import intercept_server
from grpc_opentracing import open_tracing_server_interceptor

_port    = 9082 if (os.environ.get("PORT") is None) else os.environ.get("PORT")
_msg     = "Grpc Hello" if (os.environ.get("MESSAGE") is None) else os.environ.get("MESSAGE")
_service = os.path.basename(__file__).split('.')[0]
_one_day_in_seconds = 60 * 60 * 24

tracer = init_jaeger_tracer(_service)

def formatter(name, context):
    span = context.get_active_span()
    with tracer.start_active_span("formatter", child_of=span) as scope:
        return '{}, {}!'.format(_msg, name)

class Greeter(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        msg=formatter(request.name, context)
        return greeter_pb2.HelloReply(message=msg)

def serve():
    interceptor = open_tracing_server_interceptor(tracer)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server = intercept_server(server, interceptor)

    greeter_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('0.0.0.0:{}'.format(_port))
    server.start()

    try:
        while True:
            sleep(_one_day_in_seconds)
    except KeyboardInterrupt:
        server.stop(0)

    tracer.close()

if __name__ == '__main__':
    logging.basicConfig()
    serve()
