import grpc
from concurrent import futures
from grpc_server import MetadataServiceServicer
import proto.metadata_pb2_grpc as pb2_grpc
import subprocess
import os

# Generar código gRPC automáticamente
subprocess.run("python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. ./proto/metadata.proto", shell=True)

server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
pb2_grpc.add_MetadataServiceServicer_to_server(MetadataServiceServicer(), server)
server.add_insecure_port("[::]:50051")
server.start()
print("Metadata Service running on port 50051")
server.wait_for_termination()

