import random

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizAnswer
from backend.src.services.redis import SessionData, get_session_data
from backend.src.utils.serializers import (
    check_for_multiple_source_words,
    check_for_multiple_translations,
    delete_explanations,
    delete_words_without_translation,
    serialize_according_to_the_lang, slice_dict,
)
from backend.src.utils.spreadsheets_data import get_sheet_data, get_sheet_data_by_name
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
    clean_data = delete_explanations(shown_data)
    functions = (
        delete_words_without_translation,
        check_for_multiple_translations,
    )
    for func in functions:
        shown_data = func(shown_data)
        clean_data = func(clean_data)

    combined = list(zip(shown_data.keys(), clean_data.keys()))
    random.shuffle(combined)
    shown_data_keys, clean_data_keys = zip(*combined)
    shown_data_keys = tuple(shown_data_keys)
    clean_data_keys = tuple(clean_data_keys)
    session_data["from_lang"] = from_lang
    session_data["shown_data"] = shown_data
    session_data["clean_data"] = clean_data
    session_data["quiz_keys"] = shown_data_keys
    session_data["clean_data_keys"] = clean_data_keys
    session_data["amount_of_questions"] = len(clean_data)
    session_data["correct_answers"] = 0
    await session_data.save()
    url = request.url_for("get_question", index=0)
    return RedirectResponse(url, status_code=status.HTTP_302_FOUND)


@quiz_router.get("/quiz/question/{index}")
async def get_question(
    index: int, request: Request, session_data: SessionData = Depends(get_session_data)
):
    session_data["current_index"] = index
    shown_data = session_data.get("shown_data")
    if not shown_data:
        url = request.url_for("start")
        return RedirectResponse(url, status_code=status.HTTP_302_FOUND)
    quiz_keys = session_data.get("quiz_keys")
    if index + 1 > len(quiz_keys):
        url = request.url_for("get_quiz_results")
        return RedirectResponse(url, status_code=status.HTTP_302_FOUND)

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
    from_lang = session_data.get("from_lang")
    clean_answer = delete_explanations(answer.answer.lower().strip())
    clean_answer = serialize_according_to_the_lang(from_lang, (clean_answer,))[0]
    current_index = session_data.get("current_index")
    shown_data = session_data.get("shown_data")
    clean_data = session_data.get("clean_data")

    if not clean_data:
        url = request.url_for("start")
        return RedirectResponse(url, status_code=status.HTTP_302_FOUND)

    quiz_keys = session_data.get("quiz_keys")
    clean_data_keys = session_data.get("clean_data_keys")

    current_shown_data_key = quiz_keys[current_index]
    current_clean_data_key = clean_data_keys[current_index]

    current_shown_source_word = check_for_multiple_source_words(current_shown_data_key)
    current_value = shown_data[current_shown_data_key]
    clean_translations = clean_data[current_clean_data_key]
    clean_translations = serialize_according_to_the_lang(from_lang, clean_translations)

    is_correct_option = clean_answer in clean_translations
    answers = ()
    if "," in clean_answer:
        answers = tuple(map(str.strip, clean_answer.split(",")))
    elif "/" in clean_answer:
        answers = tuple(map(str.strip, clean_answer.split("/")))

    if answers:
        answers = serialize_according_to_the_lang(from_lang, answers)
        is_correct_option = any(ans in clean_translations for ans in answers)

    if is_correct_option:
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
            "is_correct": is_correct_option,
        },
    )


@quiz_router.get("/quiz/end")
async def get_quiz_results(
    request: Request, session_data: SessionData = Depends(get_session_data)
):
    amount_of_questions = session_data.get("amount_of_questions")
    correct_answers = session_data.get("correct_answers", 0)
    return templates.TemplateResponse(
        name="end.html",
        request=request,
        context={
            "amount_of_questions": amount_of_questions,
            "correct_answers": correct_answers,
        },
    )
