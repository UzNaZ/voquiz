import re
from typing import Literal

from backend.values import AllRegexes, Spreadsheets

AnswerOrAnswers = str | tuple
UkAndEnWords = dict[AnswerOrAnswers, AnswerOrAnswers]


def check_for_multiple_translations(
    spreadsheet_data: dict[str, str]
) -> UkAndEnWords:
    """
    Converts comma-separated values in the dictionary into tuples to support multiple translations.

    :param spreadsheet_data: A dictionary where both keys and values are strings representing single words or phrases.
    :return: A dictionary where keys and/or values may be tuples if multiple entries were present.
    """
    result = {}
    for source_word, translated_word in spreadsheet_data.items():
        if "," in translated_word:
            translated_words = tuple(
                word.strip() for word in translated_word.split(",")
            )
        elif "/" in translated_word:
            translated_words = tuple(
                word.strip() for word in translated_word.split("/")
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
    source_word: str
) -> tuple[str, ...]:
    if "," in source_word:
        source_words = tuple(word.strip() for word in source_word.split(","))
    elif "/" in source_word:
        source_words = tuple(word.strip() for word in source_word.split("/"))
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

    return dict(dict_items_list[start - 1: end])


def remove_gender_endings(words: tuple[str, ...]) -> tuple[str, ...]:
    """
    Removes gender endings from each word in a given array.

    This function iterates through each word in the input array and removes ukrainian gender
    endings ("ий", "а", "о").

    :param words: The input tuple, which may contain one or more words.
    :return: A new tuple containing words with gender endings removed.
    """
    processed_words = []
    for word in words:
        for ending in ["ий", "а", "е", "о"]:
            if word.endswith(ending):
                processed_words.append(word[: -len(ending)])
    if not processed_words:
        processed_words = words
    return tuple(processed_words)


def remove_function_words(words: tuple[str, ...]) -> tuple[str, ...]:
    processed_words = []
    for word in words:
        for func_word in ["to ", "а ", "an ", "the "]:
            if word.startswith(func_word):
                processed_words.append(word.replace(func_word, ""))
            else:
                processed_words.append(word)
    return tuple(processed_words)


def serialize_according_to_the_lang(from_lang: Literal["en", "uk"], words: tuple[str, ...]) -> tuple[str, ...]:
    if from_lang == "en":
        words = remove_gender_endings(words)
    else:
        words = remove_function_words(words)
    return words
