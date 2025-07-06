from typing import Literal

from pydantic import BaseModel, Field

from backend.values import AllRegexes


class QuizData(BaseModel):
    url: str = Field(
        ..., pattern=AllRegexes.SPREADSHEET_LINK
    )
    from_row_to_row: tuple[int, int]
    from_lang: Literal["uk", "en"]


class QuizAnswer(BaseModel):
    answer: str
