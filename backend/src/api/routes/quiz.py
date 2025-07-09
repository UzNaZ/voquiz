import random

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizAnswer
from backend.src.services.redis import SessionData, get_session_data
from backend.src.utils.serializers import (check_for_multiple_source_words,
                                           check_for_multiple_translations,
                                           delete_explanations,
                                           delete_words_without_translation,
                                           slice_dict)
from backend.src.utils.spreadsheets_data import (get_sheet_data,
                                                 get_sheet_data_by_name)
from backend.src.utils.validators import validate_quiz_answer

quiz_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@quiz_router.get("/quiz")
async def start_quiz(
    request: Request, session_data: SessionData = Depends(get_session_data)
):
    quiz_data = session_data.get("quiz_data")
    url = quiz_data["url"]
    from_lang = quiz_data["from_lang"]
    sheet_name = quiz_data["sheet_name"].strip()
    if sheet_name:
        spreadsheet_data = await get_sheet_data_by_name(url, from_lang, sheet_name)
    else:
        spreadsheet_data = await get_sheet_data(url, from_lang)

    if not spreadsheet_data:
        raise ValueError("spreadsheet by this url does not exist")
    sliced_spreadsheet_data = slice_dict(
        spreadsheet_data, *quiz_data["from_row_to_row"]
    )
    shown_data = sliced_spreadsheet_data
    clean_data = delete_explanations(sliced_spreadsheet_data)
    functions = (
        check_for_multiple_translations,
        lambda x: check_for_multiple_translations(x, "/"),
        delete_words_without_translation,
    )

    for func in functions:
        shown_data = func(shown_data)
        clean_data = func(clean_data)

    combined = list(zip(list(shown_data.keys()), list(clean_data.keys())))
    random.shuffle(combined)
    shown_data_keys, clean_data_keys = zip(*combined)
    shown_data_keys = list(shown_data_keys)
    clean_data_keys = list(clean_data_keys)

    session_data["shown_data"] = shown_data
    session_data["clean_data"] = clean_data
    session_data["quiz_keys"] = shown_data_keys
    session_data["clean_data_keys"] = clean_data_keys
    session_data["amount_of_questions"] = len(clean_data)
    session_data["correct_answers"] = 0
    await session_data.save()
    url = request.url_for("get_question", index=0)
    return RedirectResponse(url, status_code=302)


@quiz_router.get("/quiz/question/{index}")
async def get_question(
    index: int, request: Request, session_data: SessionData = Depends(get_session_data)
):
    session_data["current_index"] = index
    shown_data = session_data.get("shown_data")
    if not shown_data:
        url = request.url_for("start")
        return RedirectResponse(url, status_code=302)
    quiz_keys = session_data.get("quiz_keys")
    if index + 1 > len(quiz_keys):
        correct_answers = session_data.get("correct_answers", 0)
        await session_data.clear()
        return templates.TemplateResponse(
            name="end.html",
            request=request,
            context={"correct_answers": correct_answers},
        )

    current_key = quiz_keys[index]
    current_value = shown_data[current_key]
    current_source_word = check_for_multiple_source_words(current_key)
    session_data["question_answers"] = (current_source_word, current_value)
    await session_data.save()
    return templates.TemplateResponse(
        name="quiz.html",
        request=request,
        context={
            "source_words": current_source_word,
            "translations": current_value,
            "question_number": index + 1,
            "amount_of_questions": session_data.get("amount_of_questions"),
            "is_correct": None,
        },
    )


@quiz_router.post("/quiz/answer")
async def submit_answer(
    request: Request,
    session_data: SessionData = Depends(get_session_data),
    answer: QuizAnswer = Depends(validate_quiz_answer),
):
    current_index = session_data.get("current_index")
    shown_data = session_data.get("shown_data")
    clean_data = session_data.get("clean_data")
    if not clean_data:
        url = request.url_for("start")
        return RedirectResponse(url, status_code=302)

    quiz_keys = session_data.get("quiz_keys")
    clean_data_keys = session_data.get("clean_data_keys")
    current_shown_data_key = quiz_keys[current_index]
    current_clean_data_key = clean_data_keys[current_index]
    current_shown_source_word = check_for_multiple_source_words(current_shown_data_key)
    current_value = shown_data[current_shown_data_key]
    clean_translations = clean_data[current_clean_data_key]
    if is_correct := answer.answer.lower().strip() in clean_translations:
        session_data["correct_answers"] = session_data.get("correct_answers") + 1

    await session_data.save()
    return templates.TemplateResponse(
        name="quiz.html",
        request=request,
        context={
            "source_words": current_shown_source_word,
            "translations": current_value,
            "question_number": current_index + 1,
            "amount_of_questions": session_data.get("amount_of_questions"),
            "is_correct": is_correct,
        },
    )
