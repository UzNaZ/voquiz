import os

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from backend.src.api.errors import register_exception_handlers
from backend.src.config import settings  # should be imported first
from backend.src.api.endpoints import router as api_endpoint_router


def initialize_backend_application() -> FastAPI:
    app = FastAPI()
    app.include_router(router=api_endpoint_router, prefix=settings.API_PREFIX)
    app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY"))
    register_exception_handlers(app)
    return app


backend_app: FastAPI = initialize_backend_application()
backend_app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
backend_app.mount("/images", StaticFiles(directory="frontend/images"), name="images")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app="main:backend_app", host="0.0.0.0", port=port)
