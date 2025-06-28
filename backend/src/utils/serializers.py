import re
import typing

from backend.values import AllRegexes

AnswerOrAnswers = str | frozenset
UkAndEnWords = dict[AnswerOrAnswers, AnswerOrAnswers]


def check_for_multiple_translations(
    spreadsheet_data: dict[str, str], separator: str = ","
) -> UkAndEnWords:
    spreadsheet_data = typing.cast(UkAndEnWords, spreadsheet_data)
    for en_word, uk_word in spreadsheet_data.items():
        if separator in uk_word:
            uk_words = frozenset(word.strip() for word in uk_word.split(separator))
            spreadsheet_data[en_word] = uk_words

    for en_word, uk_word in spreadsheet_data.items():
        if separator in en_word:
            en_words = frozenset(word.strip() for word in en_word.split(separator))
            spreadsheet_data[en_words] = spreadsheet_data.pop(en_word)

    return spreadsheet_data


def delete_explanations(obj: any) -> any:
    if isinstance(obj, str):
        return re.sub(AllRegexes.WORD_IN_PARENTHESES, "", obj)

    elif isinstance(obj, frozenset):
        return frozenset(delete_explanations(item) for item in obj)

    elif isinstance(obj, dict):
        return {
            delete_explanations(key): delete_explanations(value)
            for key, value in obj.items()
        }


def delete_words_without_translation(data: UkAndEnWords):
    return {word: translation for word, translation in data.items() if translation}
