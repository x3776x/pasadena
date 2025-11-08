import asyncio
import grpc
from concurrent import futures
from sqlalchemy import create_engine  # ✅ Engine sincrónico
from models.song_model import Base
from database import engine  # Este es el async engine

from proto import metadata_pb2_grpc as pb2_grpc
from metadata_service import MetadataServiceServicer


def create_tables_sync():
    """Crea las tablas usando un engine sincrónico."""
    from sqlalchemy import create_engine
    sync_engine = create_engine("postgresql://papu:CocteauTwins@postgres_metadata_db:5432/postgres_metadata_db")
    Base.metadata.create_all(bind=sync_engine)
    print("✅ Tablas creadas (modo sincrónico)")


async def serve():
    create_tables_sync()  # 🗃️ Crea las tablas antes de levantar gRPC

    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_MetadataServiceServicer_to_server(MetadataServiceServicer(), server)
    server.add_insecure_port("[::]:50051")

    await server.start()
    print("🚀 MetadataService escuchando en puerto 50051")

    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
