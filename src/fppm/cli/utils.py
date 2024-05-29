def is_valid_name(word: str):
    invalid_characters = [
        "#",
        "%",
        "&",
        "{",
        "}",
        "/",
        "\\",
        "<",
        ">",
        "*",
        "?",
        " ",
        "$",
        "!",
        "'",
        '"',
        ":",
        "@",
        "+",
        "`",
        "|",
        "=",
    ]
    for char in invalid_characters:
        if isinstance(word, str) and char in word:
            return char
        if not isinstance(word, str):
            raise ValueError("Incorrect usage of is_valid_name")
    return "valid"