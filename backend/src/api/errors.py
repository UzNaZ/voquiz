from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

templates = Jinja2Templates(directory="frontend/templates")


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return templates.TemplateResponse(
            name="error.html",
            request=request,
            context={"status_code": exc.status_code},
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return templates.TemplateResponse(
            name="error.html",
            request=request,
            context={"status_code": 500},
            status_code=500,
        )