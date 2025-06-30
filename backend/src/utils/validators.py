from typing import Literal

from fastapi import Form

from backend.src.models.schemas.pydantic_schemas.quiz_data import QuizData, QuizAnswer


async def validate_quiz_form(
    url: str = Form(...),
    from_row: int = Form(...),
    to_row: int = Form(...),
    from_lang: Literal["en", "uk"] = Form(...),
) -> QuizData:
    return QuizData(
        url=url,
        from_row_to_row=(from_row, to_row),
        from_lang=from_lang,
    )


async def validate_quiz_answer(answer: str = Form(...)) -> QuizAnswer:
    return QuizAnswer(answer=answer)
