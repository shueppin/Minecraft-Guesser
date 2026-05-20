import logging
import re
from data_scraper.cleanup_text import remove_escaped_chars


def _remove_edition_keywords(text: str) -> str:
    # Ordered keywords
    keywords_to_remove = [
        "JE:", "(Java Edition)", "Java Edition:", "Java Edition", "(Java)", "Java:", "Java",
        "BE:", "(Bedrock Edition)", "Bedrock Edition:", "Bedrock Edition", "(Bedrock)", "Bedrock:", "Bedrock",
    ]
    for keyword in keywords_to_remove:
        text = text.replace(keyword, "")

    return text.strip()


def get_java_edition_part(text: str) -> str:
    """
    Extract the value corresponding to the Java Edition part. Extracts the part between the Java identifier and the bedrock identifier.
    If the important info is in the beginning, before the identifier, it will be lost: "Yes (JE: 60, BE: 30)" --> "60,"

    Example:
        "JE: No\nBE: Yes" --> "No"
        "Java Edition: No\nBedrock Edition: Yes" --> "No"
        "Only in Java Edition" --> "Only in"
        "Only in Bedrock Edition" --> ""
        "Yes\n  JE: No\nBE: Yes" --> "No"
        "No (Java Edition)\nYes (Bedrock Edition)" --> "No"
    """
    checking_text = text.strip().lower()

    before_java = ["JE:", "Java Edition:", "Java:"]
    before_bedrock = ["BE:", "Bedrock Edition:", "Bedrock:"]

    after_java = ["(JE)", "(Java Edition)", "(Java)", "Java Edition", "Java"]
    after_bedrock = ["(BE)", "(Bedrock Edition)", "(Bedrock)", "Bedrock Edition", "Bedrock"]

    def find_index(words: list[str]) -> int:
        """Return index of first matching keyword, or -1."""
        for word in words:
            index = checking_text.find(word.lower())
            if index != -1:
                return index
        return -1

    java_index = find_index(before_java)
    bedrock_index = find_index(before_bedrock)

    # Keywords appear before the value (e.g. "JE: Yes")
    if java_index != -1 and bedrock_index != -1:
        end = bedrock_index if java_index < bedrock_index else len(text)
        return _remove_edition_keywords(text[java_index:end])

    java_index = find_index(after_java)
    bedrock_index = find_index(after_bedrock)

    # Keywords appear after the value (e.g. "Yes (Java Edition)")
    if java_index < bedrock_index:
        start = 0 if java_index != -1 else bedrock_index
        end = java_index if java_index != -1 else len(text)
        return _remove_edition_keywords(text[start:end])

    if java_index > bedrock_index:
        start = 0 if bedrock_index == -1 else bedrock_index
        return _remove_edition_keywords(text[start:java_index])

    return text


def extract_first_yes_no_partial(text: str, hardcoded_values_dict: dict=None) -> str | bool:
    """
    Try to use this through the parser
    """
    if hardcoded_values_dict is None:
        hardcoded_values_dict = {}

    if text in hardcoded_values_dict:
        return hardcoded_values_dict[text]

    java_edition_part = get_java_edition_part(remove_escaped_chars(text)).lower()

    """Extract first status token among Yes/No/Partial."""
    match = re.search(r"(Yes|No|Partial)", java_edition_part, flags=re.IGNORECASE)
    if not match:
        return "Unknown"

    first_occurred_word = match.group(1).lower()
    output_values = {"yes": True, "no": False, "partial": "Partial"}
    return output_values[first_occurred_word]


def extract_first_number(text: str) -> float:
    text = text.replace(",", "")  # Fixes values like 1,200 to be 1200
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else 0.0


def extract_all_from_word_list(text: str, word_list: list, case_sensitive=True) -> list:
    output = []

    if case_sensitive:
        for word in word_list:
            if word in text:
                output.append(word)
    else:
        for word in word_list:
            if word.lower() in text.lower():
                output.append(word)

    return output


def extract_stack_size(text: str) -> int:
    """Extract stack size from patterns like 'Yes (64)' -> 64."""
    java_edition_part = get_java_edition_part(remove_escaped_chars(text))
    match = re.search(r"\((\d+)\)", java_edition_part)
    return int(match.group(1)) if match else 1


class DataParser:
    """
    This is a wrapper for important functions that can now be accessed simply using the key
    """
    def __init__(self, data_dict: dict):
        self.data_dict = data_dict

    def get_raw(self, key = "") -> str:
        if not key:
            return ""
        output: str = self.data_dict.get(key, "")
        if not output:
            logging.warning(f"Key {key} not found in {self.data_dict}")
            return ""
        return str(output)

    def extract_all_from_word_list(self, key: str, word_list: list, case_sensitive=True) -> list:
        return extract_all_from_word_list(self.get_raw(key), word_list, case_sensitive=case_sensitive)

    def extract_first_number(self, key: str) -> float:
        return extract_first_number(self.get_raw(key))

    def extract_first_yes_no_partial(self, key: str, hardcoded_values_dict: dict = None) -> str:
        return extract_first_yes_no_partial(self.get_raw(key), hardcoded_values_dict)

    def extract_stack_size(self, key: str) -> int:
        return extract_stack_size(self.get_raw(key))