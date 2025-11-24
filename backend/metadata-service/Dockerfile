FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

# Instalar dependencias del proyecto y grpcio-tools
RUN pip install --no-cache-dir -r requirements.txt grpcio-tools

# Copiar todo el código (incluye proto, models, services, etc.)
COPY ./app ./app

# Entrar a la carpeta app
WORKDIR /app/app

# Crear carpeta para archivos de música
RUN mkdir -p /data/music

# Compilar automáticamente los archivos .proto
RUN python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    ./proto/*.proto


# Configurar PYTHONPATH para que Python encuentre los módulos generados
ENV PYTHONPATH=/app/app

# Ejecutar migraciones (solo si existen) y luego iniciar el servicio
CMD sh -c "if [ -d alembic ] && [ -f alembic.ini ]; then python -m alembic upgrade head; else echo 'No migrations found'; fi && python main.py"

