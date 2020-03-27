from grpc_tools import protoc

protoc.main(('', '-Iprotos', '--python_out=lib', '--grpc_python_out=lib',
             'protos/greeter.proto'))
