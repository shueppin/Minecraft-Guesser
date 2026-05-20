from html import unescape
import re


def remove_escaped_chars(text: str) -> str:
    """Normalize whitespace and decode HTML entities."""
    text = text.replace('\u200b', ' ')
    text = text.replace('\u200c', ' ')
    text = text.replace('\xa0', ' ')
    return re.sub(r"\s+", " ", unescape(text)).strip()
