from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api_v1 import router

app = FastAPI(
    title="Backend for serve and managing Jars by Monobank",
    version="0.1",
)

# Дозволити CORS для всього API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", reload=True)
    except KeyboardInterrupt:
        print("Server stopped")