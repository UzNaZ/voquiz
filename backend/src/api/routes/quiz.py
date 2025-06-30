from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizAnswer
from backend.src.utils.serializers import (check_for_multiple_translations,
                                           delete_explanations,
                                           delete_words_without_translation,
                                           slice_dict, check_for_multiple_source_words)
from backend.src.utils.spreadsheets_data import get_sheet_data

quiz_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@quiz_router.get("/quiz")
async def start_quiz(request: Request):
    quiz_data = request.session.get("quiz_data")

    url = quiz_data["url"]
    from_lang = quiz_data["from_lang"]
    spreadsheet_data = await get_sheet_data(url, from_lang)
    if not spreadsheet_data:
        raise ValueError("spreadsheet by this url does not exist")
    sliced_spreadsheet_data = slice_dict(
        spreadsheet_data, *quiz_data["from_row_to_row"]
    )
    serialized_data = check_for_multiple_translations(sliced_spreadsheet_data)
    serialized_data = check_for_multiple_translations(serialized_data, "/")
    shown_data = delete_words_without_translation(serialized_data)
    clean_data = delete_explanations(serialized_data)
    request.session["shown_data"] = shown_data
    request.session["clean_data"] = clean_data
    request.session["quiz_keys"] = list(clean_data.keys())
    request.session["amount_of_questions"] = len(clean_data)
    url = request.url_for("get_question", index=0)
    return RedirectResponse(url, status_code=302)


@quiz_router.get("/quiz/question/{index}")
async def get_question(index: int, request: Request):
    shown_data = request.session.get("shown_data")
    # if not shown_data:
    #     url = request.url_for("start")
    #     return RedirectResponse(url, status_code=302)

    quiz_keys = request.session.get("quiz_keys")
    if index + 1 > len(quiz_keys):
        return templates.TemplateResponse(name="end.html", request=request)

    current_key = check_for_multiple_source_words(quiz_keys[index])
    current_value = tuple(shown_data[current_key])
    request.session["question_answers"] = (current_key, current_value)
    return templates.TemplateResponse(
        name="quiz.html",
        request=request,
        context={
            "source_words": current_key,
            "translations": current_value,
            "question_number": index + 1,
            "amount_of_questions": request.session.get("amount_of_questions"),
        },
    )


@quiz_router.post("/quiz/answer")
async def submit_answer(request: Request, answer: QuizAnswer):
    translations = request.session.get("question_answers")[1]
    is_correct = answer.answer in translations
    index = request.session.get("current_index", 0)
    request.session["current_index"] = index + 1
    return {
        "is_correct": is_correct,
    }
