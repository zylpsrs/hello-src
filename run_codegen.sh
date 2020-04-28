#! /bin/bash

python3 -m grpc_tools.protoc -Iprotos \
        --python_out=lib --grpc_python_out=lib protos/greeter.proto

perl -i -ne 's/import greeter_pb2/import lib.greeter_pb2/g;print' greeter_pb2_grpc.py
