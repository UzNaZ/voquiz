import csv
import re
from io import StringIO

import httpx


def get_spreadsheet_id(link: str):
    if m := re.search(r"/spreadsheets/d/([A-Za-z0-9-_]+)", link):
        spreadsheet_id = m.group(1)
        return spreadsheet_id


async def get_sheet_id(link: str):
    if m := re.search(r"/spreadsheets/d/[A-Za-z0-9-_]+/edit\?gid=([0-9]+)", link):
        gid = m.group(1)
        return gid


async def get_sheet_data(link: str):
    spreadsheet_id = get_spreadsheet_id(link)
    sheet_id = await get_sheet_id(link)

    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={sheet_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

    f = StringIO(response.text)
    reader = csv.reader(f)
    result = []

    for row in reader:
        result.append({row[1]: row[3]})

    return result


async def get_sheet_data_by_name(link: str, sheet_name: str):
    spreadsheet_id = get_spreadsheet_id(link)
    url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

    data = StringIO(response.text)
    reader = csv.reader(data)
    result = []

    for row in reader:
        result.append({row[1]: row[3]})

    return result
