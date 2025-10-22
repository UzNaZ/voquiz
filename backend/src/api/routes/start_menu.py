from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizData
from backend.src.services.redis import SessionData, get_session_data
from backend.src.utils.validators import validate_quiz_form

menu_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@menu_router.get("/")
async def start(
    request: Request,
    session_data: SessionData = Depends(get_session_data),
):
    await session_data.clear()
    return templates.TemplateResponse(name="home.html", request=request)


@menu_router.post("/")
async def send_quiz_data(
    request: Request,
    session_data: SessionData = Depends(get_session_data),
    quiz_data: QuizData = Depends(validate_quiz_form),
):
    session_data["quiz_data"] = quiz_data.model_dump()
    await session_data.save()
    url = request.url_for("start_quiz")
    response = RedirectResponse(url, status_code=302)
    session_data.set_cookie_on(response)
    return response
