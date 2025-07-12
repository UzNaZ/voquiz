import re

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


def slice_dict(dict_obj: dict, start: int, stop: int) -> dict:
    """
    Removes entries from the dictionary where the source word or translation value is empty.

    :param dict_obj: a dict instance you want to slice
    :param start: starting point
    :param stop: finishing point
    :return: A filtered dictionary excluding entries without the source word or translations.
    """
    dict_len = len(dict_obj.items())
    if stop > dict_len:
        stop = dict_len

    if stop - start > Spreadsheets.MAX_QUESTIONS:
        stop = start + Spreadsheets.MAX_QUESTIONS

    return dict(list(dict_obj.items())[start - 1:stop])
