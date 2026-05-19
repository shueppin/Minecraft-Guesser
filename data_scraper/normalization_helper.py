import logging


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

    def get_float(self, key = "", complex_extraction_dict: dict = None) -> float:
        original_value = self.get_raw(key).replace(",", "")  # Fixes values like 1,200
        try:
            return float(original_value)
        except ValueError:
            if complex_extraction_dict is not None:
                return complex_extraction_dict.get(original_value, 0.0)
            return 0.0

    def get_int(self, key = "", complex_extraction_dict: dict = None) -> int:
        value = self.get_raw(key).replace(",", "")  # Fixes values like 1,200
        try:
            return int(value)
        except ValueError:
            if complex_extraction_dict is not None:
                return complex_extraction_dict.get(key, 0)
            return 0

    def get_normalized_string(self, key = "") -> str:
        value = self.get_raw(key)
        return value.strip().lower()
