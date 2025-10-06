# streaming-service/Dockerfile
FROM python:3.11-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y código
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app

# Puerto donde corre FastAPI
EXPOSE 8003

# Comando para iniciar el servicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
