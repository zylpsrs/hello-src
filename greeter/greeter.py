from concurrent import futures
import os
import logging
from time import sleep

from grpc_opentracing import open_tracing_server_interceptor
from grpc_opentracing.grpcext import intercept_server

import grpc
from lib import greeter_pb2
from lib import greeter_pb2_grpc

from lib.tracing import init_tracer

_port = 9082 if (os.environ.get("PORT") is None) else os.environ.get("PORT")

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def formatter(name, context):
    span = context.get_active_span()
    with tracer.start_active_span("formatter", child_of=span) as scope:
        return 'Grpc Hello, {}!'.format(name)

class Greeter(greeter_pb2_grpc.GreeterServicer):
    def SayHello(self, request, context):
        msg=formatter(request.name, context)
        return greeter_pb2.HelloReply(message=msg)

tracer = init_tracer("greeter")

def serve():
    interceptor = open_tracing_server_interceptor(tracer)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    server = intercept_server(server, interceptor)

    greeter_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('0.0.0.0:{}'.format(_port))
    server.start()

    try:
        while True:
            sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print('Stop server', flush=True)
        tracer.close()
        server.stop(0)

if __name__ == '__main__':
    logging.basicConfig()
    serve()
