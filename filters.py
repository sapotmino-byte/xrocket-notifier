from config import COMPILED_KEYWORDS, COMPILED_SPAM


def is_important(text) -> bool:
    if not text:
        return False
    lowered = text.lower()

    for spam in COMPILED_SPAM:
        if spam.search(lowered):
            return False

    for pattern in COMPILED_KEYWORDS:
        if pattern.search(lowered):
            return True

    return False


def get_clean_text(text) -> str:
    """Вырезает HTML-теги и убирает лишние переносы."""
    import re
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
