from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from backend.src.utils.serializers import (check_for_multiple_translations,
                                           check_for_parentheses)
from backend.src.utils.spreadsheets_data import get_sheet_data

quiz_router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")


@quiz_router.get("/quiz/question/{index}")
async def get_question(index: int, request: Request):
    quiz_data = request.session.get("quiz_data")
    if not quiz_data:
        url = request.url_for("start")
        return RedirectResponse(url, status_code=302)

    url = quiz_data["url"]
    from_row_to_row = quiz_data["from_row_to_row"]
    from_lang_to_lang = quiz_data["from_lang_to_lang"]
    spreadsheet_data = await get_sheet_data(url)
    serialized_data = check_for_parentheses(spreadsheet_data)
    serialized_data = check_for_multiple_translations(spreadsheet_data)
