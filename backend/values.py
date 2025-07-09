from dataclasses import dataclass


@dataclass(frozen=True)
class Spreadsheets:
    GET_BY_GID_URL = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid={gid}"
    GET_BY_NAME_URL = "https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    EN_COLUMN_NUMBER = 1
    UK_COLUMN_NUMBER = 3
    ID_FROM_URL_GROUP = 1
    MAX_QUESTIONS = 100


@dataclass(frozen=True)
class AllRegexes:
    SPREADSHEET_LINK = (
        r"^https://docs\.google\.com/spreadsheets/d/[\w-]+(?:/[^\s?#]*)?(?:\?[^#]*)?$"
    )
    URL_HAS_SHEET_ID = r"/spreadsheets/d/[\w-]+(?:/[^\s?#]*)?(?:\?[^#]*)?.*gid=\d+"
    URL_HAS_SPREADSHEET_ID = r"/spreadsheets/d/([A-Za-z0-9-_]+)"
    WORD_IN_PARENTHESES = r"\(.*?\)"


@dataclass(frozen=True)
class RedisData:
    SESSION_COOKIE_NAME: str = "session_id"
    SESSION_EXPIRE_IN_2_HOURS: int = 60 * 60 * 2
