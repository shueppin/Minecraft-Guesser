import logging
import re
from html import unescape


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
        "Java Edition: No\nBedrock Edition: Yes" --> No
        "Only in Java Edition" --> "Only in"
        "Only in Bedrock Edition" --> ""
        "Yes\n  JE: No\nBE: Yes" --> "No"
        "No (Java Edition)\nYes (Bedrock Edition)" --> "No"
    """
    # Check whether we have an index for a Java word and a Bedrock word
    checking_text = text.strip().lower()

    java_edition_index = -1
    bedrock_edition_index = -1

    # Check if any of the words that are BEFORE THE VALUE exist
    for word in ["JE:", "Java Edition:", "Java:"]:  # Words are checked with this priority
        if word.lower() in checking_text:
            java_edition_index = checking_text.index(word.lower())
            break

    for word in ["BE:", "Bedrock Edition:", "Bedrock:"]:
        if word.lower() in checking_text:
            bedrock_edition_index = checking_text.index(word.lower())
            break

    # If both are not -1, then take the value
    if java_edition_index != -1 and bedrock_edition_index != -1:
        if java_edition_index < bedrock_edition_index:
            return _remove_edition_keywords(text[java_edition_index:bedrock_edition_index])
        else:
            return _remove_edition_keywords(text[java_edition_index:])

    # Check if any of the words that are AFTER THE VALUE exist
    for word in ["(JE)", "(Java Edition)", "(Java)", "Java Edition", "Java"]:  # Words are checked with this priority
        if word.lower() in checking_text:
            java_edition_index = checking_text.index(word.lower())
            break

    for word in ["(BE)", "(Bedrock Edition)", "(Bedrock)", "Bedrock Edition", "Bedrock"]:
        if word.lower() in checking_text:
            bedrock_edition_index = checking_text.index(word.lower())
            break

    # Consider that the values probably appear after the index
    if java_edition_index < bedrock_edition_index:
        if java_edition_index == -1:
            return _remove_edition_keywords(text[bedrock_edition_index:])
        else:
            return _remove_edition_keywords(text[:java_edition_index])

    elif java_edition_index > bedrock_edition_index:
        if bedrock_edition_index == -1:
            return _remove_edition_keywords(text[:java_edition_index])
        else:
            return _remove_edition_keywords(text[bedrock_edition_index:java_edition_index])

    return text


def get_first_yes_no_partial(text: str, hardcoded_values_dict: dict=None) -> str | bool:
    """
    Try to use this through the parser
    """
    if hardcoded_values_dict is None:
        hardcoded_values_dict = {}

    if text in hardcoded_values_dict:
        return hardcoded_values_dict[text]

    java_edition_part = get_java_edition_part(clean_text(text)).lower()

    # Go through all words and find the word that occurs first
    first_occurrence_index = -1
    first_occurred_word = "unknown"

    for word in ["yes", "no", "partial"]:
        if word in java_edition_part:
            index = java_edition_part.index(word)

            if index < first_occurrence_index or first_occurrence_index == -1:
                first_occurrence_index = index
                first_occurred_word = word

    # Return the value of the first occurred word
    output_values = {"yes": True, "no": False, "partial": "Partial", "unknown": "Unknown"}
    return output_values[first_occurred_word]


def clean_text(text: str) -> str:
    """Normalize whitespace and decode HTML entities."""
    text = text.replace('\u200c', ' ')
    text = text.replace('\xa0', ' ')
    return re.sub(r"\s+", " ", unescape(text)).strip()


class DataParser:
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

    def get_boolean(self, key = "") -> bool:
        value = self.get_raw(key)
        if value.lower() == "yes":
            return True
        elif value.lower() == "no":
            return False
        else:
            return False

    def get_first_float(self, key = "") -> float:
        value = self.get_raw(key).replace(",", "")  # Fixes values like 1,200 to be 1200

        match = re.search(r"\d+(?:\.\d+)?", value)

        return float(match.group(0)) if match else 0.0

    def get_first_int(self, key = "", complex_extraction_dict: dict = None) -> int:
        value = self.get_raw(key).replace(",", "")  # Fixes values like 1,200 to be 1200

        match = re.search(r"\d+(?:\.\d+)?", value)

        return round(float(match.group(0))) if match else 0

    def get_normalized_string(self, key = "") -> str:
        value = self.get_raw(key)
        return value.strip().lower()

    def get_all_from_word_list(self, word_list: list, key = "", case_sensitive=True) -> list:
        value = self.get_raw(key)

        output = []

        if case_sensitive:
            for word in word_list:
                if word in value:
                    output.append(word)
        else:
            for word in word_list:
                if word.lower() in value.lower():
                    output.append(word)

        return output

    def get_first_yes_no_partial(self, key: str, hardcoded_values_dict: dict = None) -> str:
        if hardcoded_values_dict is None:
            hardcoded_values_dict = {}
        value = self.get_raw(key)

        return get_first_yes_no_partial(value, hardcoded_values_dict)