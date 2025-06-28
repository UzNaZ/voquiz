import asyncio
import csv
import re
from io import StringIO

import httpx

from backend.src.utils.serializers import (check_for_multiple_translations,
                                           delete_explanations,
                                           delete_words_without_translation)
from backend.values import AllRegexes, Spreadsheets


def get_spreadsheet_id(link: str):
    if matches := re.search(AllRegexes.URL_HAS_SPREADSHEET_ID, link):
        spreadsheet_id = matches.group(Spreadsheets.ID_FROM_URL_GROUP)
        return spreadsheet_id


async def get_sheet_id(link: str):
    if matches := re.search(AllRegexes.URL_HAS_SHEET_ID, link):
        gid = matches.group(Spreadsheets.ID_FROM_URL_GROUP)
        return gid


async def get_sheet_data(link: str):
    spreadsheet_id = get_spreadsheet_id(link)
    sheet_id = await get_sheet_id(link)

    url = Spreadsheets.GET_BY_GID_URL.format(
        spreadsheet_id=spreadsheet_id, gid=sheet_id
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

    data = StringIO(response.text)
    reader = csv.reader(data)
    result = {}

    for row in reader:
        result[row[Spreadsheets.UK_COLUMN_NUMBER]] = row[Spreadsheets.EN_COLUMN_NUMBER]

    return result


async def get_sheet_data_by_name(link: str, sheet_name: str):
    spreadsheet_id = get_spreadsheet_id(link)
    url = Spreadsheets.GET_BY_NAME_URL.format(
        spreadsheet_id=spreadsheet_id, sheet_name=sheet_name
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    data = StringIO(response.text)
    reader = csv.reader(data)
    result = {}

    for row in reader:
        result[row[Spreadsheets.UK_COLUMN_NUMBER]] = row[Spreadsheets.EN_COLUMN_NUMBER]

    return result
