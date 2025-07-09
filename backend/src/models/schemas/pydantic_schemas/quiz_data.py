import re
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from backend.values import AllRegexes


class QuizData(BaseModel):
    url: str = Field(..., pattern=AllRegexes.SPREADSHEET_LINK)
    sheet_name: str = Field(default="")
    from_row_to_row: tuple[int, int]
    from_lang: Literal["uk", "en"]

    @model_validator(mode="after")
    def validate_url_and_sheet_requirements(self) -> "QuizData":
        """
        Validates that either the URL contains a gid parameter OR a sheet_name is provided.
        Both cannot be empty when gid is missing from the URL.
        """
        url_has_gid = re.search(AllRegexes.URL_HAS_SHEET_ID, self.url)
        url_is_valid_spreadsheet = re.match(AllRegexes.SPREADSHEET_LINK, self.url)
        print(self.sheet_name.strip())
        if not url_has_gid and not url_is_valid_spreadsheet:
            raise ValueError("Invalid Google Sheets URL format")

        if not url_has_gid and not self.sheet_name.strip():
            raise ValueError(
                "Sheet name is required when URL doesn't contain gid parameter"
            )

        return self


class QuizAnswer(BaseModel):
    answer: str
