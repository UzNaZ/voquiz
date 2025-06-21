from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

menu_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@menu_router.get("/")
async def start(request: Request):
    return templates.TemplateResponse(name="home.html", context={"request": request})
