from typing import Literal

from fastapi import Form

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizAnswer, QuizData


async def validate_quiz_form(
    url: str = Form(...),
    sheet_name: str = Form(default=""),
    from_row: int = Form(...),
    to_row: int = Form(...),
    from_lang: Literal["en", "uk"] = Form(...),
) -> QuizData:
    return QuizData(
        url=url,
        sheet_name=sheet_name,
        from_row_to_row=(from_row, to_row),
        from_lang=from_lang,
    )


async def validate_quiz_answer(answer: str = Form(...)) -> QuizAnswer:
    return QuizAnswer(answer=answer)
