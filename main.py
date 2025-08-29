from fastapi import FastAPI
import uvicorn

from api_v1 import router
app = FastAPI(title="Backend for serve and managing Jars by Monobank", version="0.1",)
app.include_router(router)

if __name__ == "__main__":
    try:
        uvicorn.run("main:app", reload=True)
    except KeyboardInterrupt:
        print("Server stopped")