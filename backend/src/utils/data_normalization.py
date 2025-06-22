import re


async def check_for_multiple_uk_words(
    spreadsheet_data: list[tuple[str, str]], sep: str = ","
) -> list[tuple[str, str | list]]:
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
) -> list[tuple[str | tuple, str | tuple]]:
    edited_data = list(spreadsheet_data)
    for i, (en_word, uk_word) in enumerate(edited_data):
        if "(" in en_word:
            new_en_word = re.split(r"(\(.*?\))", en_word)
            new_en_word = tuple(
                part.strip("()").strip()
                for i, part in enumerate(new_en_word)
                if part.strip()
            )
            edited_data[i] = (new_en_word, uk_word)

    for i, (en_word, uk_word) in enumerate(edited_data):
        if "(" in uk_word:
            new_uk_word = re.split(r"(\(.*?\))", uk_word)
            new_uk_word = tuple(
                part.strip("()").strip()
                for i, part in enumerate(new_uk_word)
                if part.strip()
            )
            edited_data[i] = (en_word, new_uk_word)
            print(edited_data[i])
    return edited_data
