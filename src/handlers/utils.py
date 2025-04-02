import re


def clean_text_from_html(text: str) -> str:
    """
    Удаляет все HTML-теги из переданного текста.
    """
    return re.sub(r"<[^>]*>", "", text)
