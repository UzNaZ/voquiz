from pydantic import BaseModel


class QuizData(BaseModel):
    url: str
    from_row_to_row: tuple[int, int]
    from_lang_to_lang: tuple[str, str]
