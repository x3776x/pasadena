# app/main.py
from fastapi import FastAPI
from .streaming import router as streaming_router

app = FastAPI(title="Streaming Service")

# Incluye los endpoints de streaming
app.include_router(streaming_router, prefix="/streaming", tags=["Streaming"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
