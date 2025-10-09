FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar toda la app, incluyendo proto
COPY ./app ./app

WORKDIR /app/app

# Hacer que proto sea un paquete Python

# Crear carpeta para archivos de música
RUN mkdir -p /data/music

# Configurar PYTHONPATH para que Python encuentre proto
ENV PYTHONPATH=/app/app


# Ejecutable final
CMD ["python", "main.py"]
