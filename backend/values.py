from dataclasses import dataclass


@dataclass(frozen=True)
class SpreadSheets:
    GET_BY_GID_URL = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    GET_BY_NAME_URL = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    UK_COLUMN_NUMBER = 1
    EN_COLUMN_NUMBER = 3
    ID_FROM_URL_GROUP = 1


@dataclass(frozen=True)
class AllRegexes:
    URL_HAS_SHEET_ID = r"/spreadsheets/d/[A-Za-z0-9-_]+/edit\?gid=([0-9]+)"
    URL_HAS_SPREADSHEET_ID = r"/spreadsheets/d/([A-Za-z0-9-_]+)"
    WORD_IN_PARENTHESES = r"(\(.*?\))"
