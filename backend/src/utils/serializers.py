import re
from typing import Literal

from backend.values import AllRegexes, Spreadsheets

AnswerOrAnswers = str | tuple
UkAndEnWords = dict[AnswerOrAnswers, AnswerOrAnswers]


def check_for_multiple_translations(
    spreadsheet_data: dict[str, str], separator: str = ","
) -> UkAndEnWords:
    """
    Converts comma-separated values in the dictionary into tuples to support multiple translations.

    :param spreadsheet_data: A dictionary where both keys and values are strings representing single words or phrases.
    :param separator: The delimiter used to separate multiple translations in a single string.
    :return: A dictionary where keys and/or values may be tuples if multiple entries were present.
    """
    result = {}
    for source_word, translated_word in spreadsheet_data.items():
        if separator in translated_word:
            translated_words = tuple(
                word.strip() for word in translated_word.split(separator)
            )
        else:
            translated_words = (
                (translated_word,)
                if isinstance(translated_word, str)
                else translated_word
            )

        result[source_word] = translated_words
    return result


def check_for_multiple_source_words(
    source_word: str, separator: str = ","
) -> tuple[str, ...]:
    if separator in source_word:
        source_words = tuple(word.strip() for word in source_word.split(separator))
    else:
        source_words = (source_word,)
    return source_words


def delete_explanations(obj: any) -> any:
    """
    Recursively removes substrings in parentheses from strings, tuples, or nested dictionaries.

    :param obj: A string, tuple, or dictionary potentially containing parenthetical explanations.
    :return: The cleaned version of the object with all parenthetical substrings removed.
    """
    if isinstance(obj, str):
        return re.sub(AllRegexes.WORD_IN_PARENTHESES, "", obj).strip()

    elif isinstance(obj, tuple):
        return tuple(delete_explanations(item) for item in obj)

    elif isinstance(obj, dict):
        return {
            delete_explanations(key): delete_explanations(value)
            for key, value in obj.items()
        }


def delete_words_without_translation(spreadsheet_data: UkAndEnWords):
    """
    Removes entries from the dictionary where the source word or translation value is empty.

    :param spreadsheet_data: data received from Google Spreadsheets.
    :return: A filtered dictionary excluding entries without the source word or translations.
    """
    return {
        word: translation
        for word, translation in spreadsheet_data.items()
        if word and translation
    }


def slice_dict(dict_items_list: list[tuple[str, str]], start: int, end: int) -> dict:
    """
    Slices a dictionary according to start and end values.

    :param dict_items_list: representation of the dict you want to slice
    :param start: starting point
    :param end: finishing point
    :return: A sliced dictionary
    """
    dict_len = len(dict_items_list)
    if end > dict_len:
        end = dict_len

    if end - start > Spreadsheets.MAX_QUESTIONS:
        end = start + Spreadsheets.MAX_QUESTIONS

    return dict(dict_items_list[start - 1 : end])


def remove_gender_ending(word: str, lang: Literal["uk", "en"]) -> str:
    for ending in ["ий", "а", "о"]:
        if word.endswith(ending):
            word = word.replace(ending, "")
    return word
