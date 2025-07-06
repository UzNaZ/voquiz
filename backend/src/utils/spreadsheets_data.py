"""
This module provides utilities for downloading and processing translation word pairs
from Google Sheets documents in CSV format.

Functions:
- get_spreadsheet_id: Extracts the spreadsheet ID from a Google Sheets URL.
- get_sheet_id: Extracts the sheet (gid) ID from a Google Sheets URL.
- get_sheet_data: Fetches word pairs from a sheet using its gid,
and returns them based on the specified source language.
- get_sheet_data_by_name: Fetches word pairs from a sheet using its name,
and returns them based on the specified source language.

Depending on the `from_lang` parameter, the returned dictionary will contain either:
  - Ukrainian words as keys and English translations as values (`from_lang="uk"`), or
  - English words as keys and Ukrainian translations as values (`from_lang="en"`).
"""

import csv
import re
from io import StringIO
from typing import Literal, Optional

import httpx

from backend.values import AllRegexes, Spreadsheets


def get_spreadsheet_id(link: str):
    """
    Extracts the spreadsheet ID from a Google Sheets URL.

    :param link: A string containing the Google Sheets URL.
    :return: The spreadsheet ID as a string if found, otherwise None.
    """
    matches = re.search(AllRegexes.URL_HAS_SPREADSHEET_ID, link)
    spreadsheet_id = matches.group(Spreadsheets.ID_FROM_URL_GROUP)
    return spreadsheet_id


async def get_sheet_id(link: str):
    """
    Extracts the sheet (gid) ID from a Google Sheets URL.

    :param link: A string containing the Google Sheets URL.
    :return: The sheet ID (gid) as a string if found, otherwise None.
    """
    matches = re.search(AllRegexes.URL_HAS_SHEET_ID, link)
    gid = matches.group(Spreadsheets.ID_FROM_URL_GROUP)
    return gid


async def get_sheet_data(
    link: str, from_lang: Literal["en", "uk"]
) -> Optional[dict[str, str]]:
    """
    Retrieves translation word pairs from a Google Sheets CSV and returns them in serialization-ready format.

    :param link: The URL of the Google Sheets document.
    :param from_lang: The source language (the one shown in the quiz question).
                      If "uk", the quiz will ask Ukrainian words and expect English answers.
                      If "en", the quiz will ask English words and expect Ukrainian answers.
    :return: A dictionary where keys are words in the source language and values are their translations.
    """
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
    if from_lang == "uk":
        for row in reader:
            result[row[Spreadsheets.UK_COLUMN_NUMBER].lower()] = row[
                Spreadsheets.EN_COLUMN_NUMBER
            ].lower()
    elif from_lang == "en":
        for row in reader:
            result[row[Spreadsheets.EN_COLUMN_NUMBER].lower()] = row[
                Spreadsheets.UK_COLUMN_NUMBER
            ].lower()

    return result


async def get_sheet_data_by_name(
    link: str, sheet_name: str, from_lang: Literal["en", "uk"]
) -> Optional[dict[str, str]]:
    """
    Fetches CSV data from a Google Sheet using the spreadsheet ID and the sheet's name.

    :param link: A string containing the Google Sheets URL.
    :param sheet_name: The name of the specific sheet you want to fetch data from.
    :param from_lang: The source language (the one shown in the quiz question).
                      If "uk", the quiz will ask Ukrainian words and expect English answers.
                      If "en", the quiz will ask English words and expect Ukrainian answers.
    :return: A dictionary where keys are words in the source language and values are their translations.
    """
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
    if from_lang == "uk":
        for row in reader:
            result[row[Spreadsheets.UK_COLUMN_NUMBER].lower()] = row[
                Spreadsheets.EN_COLUMN_NUMBER
            ].lower()
    elif from_lang == "en":
        for row in reader:
            result[row[Spreadsheets.EN_COLUMN_NUMBER].lower()] = row[
                Spreadsheets.UK_COLUMN_NUMBER
            ].lower()

    return result
