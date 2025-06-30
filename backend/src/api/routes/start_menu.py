from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizData
from backend.src.utils.validators import validate_quiz_form

menu_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@menu_router.get("/")
async def start(request: Request):
    return templates.TemplateResponse(name="home.html", request=request)


@menu_router.post("/")
async def send_quiz_data(request: Request, quiz_data: QuizData = Depends(validate_quiz_form)):
    request.session["quiz_data"] = quiz_data.dict()
    url = request.url_for("start_quiz")
    return RedirectResponse(url, status_code=302)
