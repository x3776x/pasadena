from fastapi import FastAPI

app = FastAPI(title="auth-service")

@app.get("/")
async def root():
    return {"message": "Hello from Auth Service"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)