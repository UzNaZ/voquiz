from typing import Literal

from pydantic import BaseModel, Field


class QuizData(BaseModel):
    url: str = Field(
        ..., pattern=r"^https://docs\.google\.com/spreadsheets/d/\d+/.*[\?&]gid=\d+"
    )
    from_row_to_row: tuple[int, int]
    from_lang: Literal["uk", "en"]


class QuizAnswer(BaseModel):
    answer: str
