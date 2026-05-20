from html import unescape
from urllib.parse import unquote
import re


def remove_problem_chars(text: str) -> str:
    """
    Remove or replace Unicode characters and decode HTML and URL entities
    Also strips the text and collapses multiple spaces.
    """

    output_lines = []
    for line in text.splitlines():
        # Replace Zero-width characters
        line = line.replace('\u200a', ' ')
        line = line.replace('\u200b', ' ')
        line = line.replace('\u200c', ' ')
        line = line.replace('\u200d', ' ')
        line = line.replace('\u200e', ' ')
        line = line.replace('\u200f', ' ')
        line = line.replace('\xa0', ' ')  # kind of NBSP

        # Replace special characters
        line = line.replace('\u00a7', '')  # Remove §
        line = line.replace('\u00d7', 'x')  # Replace × with x (for damage numbers)
        line = line.replace('\u2013', '-')  # Replace – with -
        line = line.replace('\u2044', '/')
        line = line.replace('\u2265', '>')
        line = line.replace('\u2212', '-')
        line = line.replace('\u221e', '')  # Remove ∞

        # HTML and URL
        line = unquote(line)
        line = unescape(line)

        output_lines.append(re.sub(r"\s+", " ", line).strip())  # Collapse consecutive whitespaces

    return '\n'.join(output_lines).strip()

