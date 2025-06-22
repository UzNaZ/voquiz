import re


async def check_for_multiple_words(
    spreadsheet_data: list[tuple[str, str]], sep: str = ","
) -> list[tuple[str | list[str], str | list[str]]]:
    edited_data = list(spreadsheet_data)
    for i, (en_word, uk_word) in enumerate(edited_data):
        if sep in uk_word:
            uk_words = [word.strip() for word in uk_word.split(sep)]
            edited_data[i] = (en_word, uk_words)

    for i, (en_word, uk_word) in enumerate(edited_data):
        if sep in en_word:
            en_words = [word.strip() for word in en_word.split(sep)]
            edited_data[i] = (en_words, uk_word)

    return edited_data


async def check_for_parenthesis(
    spreadsheet_data: list[tuple[str, str]],
) -> list[tuple[str | tuple[str, ...], str | tuple[str, ...]]]:
    edited_data = list(spreadsheet_data)
    for i, (en_word, uk_word) in enumerate(edited_data):
        if "(" in en_word:
            new_en_word = split_by_parentheses(en_word)
            edited_data[i] = (new_en_word, uk_word)

    for i, (en_word, uk_word) in enumerate(edited_data):
        if "(" in uk_word:
            new_uk_word = split_by_parentheses(uk_word)
            edited_data[i] = (en_word, new_uk_word)
    return edited_data


def split_by_parentheses(text: str) -> tuple[str, ...]:
    parts = re.split(r"(\(.*?\))", text)
    return tuple(
        part.strip("()").strip()
        for part in parts
        if part.strip()
    )
