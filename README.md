# pasadena 
 Este  proyecto utiliza Python + FastAPI, PostgreSQL, MongoDB y Electron

 # Prerequisitos:
 Docker
 Python 3.11+
 Go 1.19+ 
 Node.js

# Clonar el repositorio

git clone <link>
cd pasadena

# Infraestructura 

cd backend
docker-compose up -d postgres_db mongodb

# Inicializar auth-service/metadata-service para hacer cambios 
cd auth-service or metadata-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

uvicorn app.main:app --reload --port 8001

# Para migraciones
alembic revision --autogenerate -m "descripcion_cambio"

# Para probar el sistema completo 
docker-compose up --build -d 
