import re
import typing

from backend.values import AllRegexes

WordList = list[str]
WordTuple = tuple[str, ...]
WordField = str | WordList
WordFieldWithParens = str | WordTuple

SpreadsheetRow = tuple[str, str]
SpreadsheetRowWithMultipleTranslations = tuple[WordField, WordField]
SpreadsheetRowWithParens = tuple[WordFieldWithParens, WordFieldWithParens]


def check_for_multiple_words(
    spreadsheet_data: list[SpreadsheetRow], separator: str = ","
) -> list[SpreadsheetRowWithMultipleTranslations]:
    spreadsheet_data = typing.cast(list[SpreadsheetRowWithMultipleTranslations], spreadsheet_data)
    for i, (en_word, uk_word) in enumerate(spreadsheet_data):
        if separator in uk_word:
            uk_words = [word.strip() for word in uk_word.split(separator)]
            spreadsheet_data[i] = (en_word, uk_words)

    for i, (en_word, uk_word) in enumerate(spreadsheet_data):
        if separator in en_word:
            en_words = [word.strip() for word in en_word.split(separator)]
            spreadsheet_data[i] = (en_words, uk_word)

    return spreadsheet_data


def check_for_parentheses(
    spreadsheet_data: list[SpreadsheetRow],
) -> list[SpreadsheetRowWithParens]:
    spreadsheet_data = typing.cast(list[SpreadsheetRowWithParens], spreadsheet_data)
    for i, (en_word, uk_word) in enumerate(spreadsheet_data):
        if "(" in en_word:
            new_en_word = split_by_parentheses(en_word)
            spreadsheet_data[i] = (new_en_word, uk_word)

    for i, (en_word, uk_word) in enumerate(spreadsheet_data):
        if "(" in uk_word:
            new_uk_word = split_by_parentheses(uk_word)
            spreadsheet_data[i] = (en_word, new_uk_word)
    return spreadsheet_data


def split_by_parentheses(text: str) -> WordTuple:
    parts = re.split(AllRegexes.WORD_IN_PARENTHESES, text)
    return tuple(
        part.strip("()").strip()
        for part in parts
        if part.strip()
    )
