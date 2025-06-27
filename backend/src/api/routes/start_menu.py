from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizData


menu_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@menu_router.get("/")
async def start(request: Request):
    return templates.TemplateResponse(name="home.html", context={"request": request})


@menu_router.post("/")
async def send_quiz_data(request: Request, quiz_data: QuizData):
    request.session["quiz_data"] = quiz_data.dict()
    return RedirectResponse("/quiz/question/0", status_code=302)
