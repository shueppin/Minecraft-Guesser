import json
from pathlib import Path
from typing import Any

filter_for : str = "Luminous"

# Load blocks.json
blocks_path = Path(__file__).resolve().parent / "blocks.json"
with blocks_path.open("r", encoding="utf-8") as f:
    blocks = json.load(f)

found_elements : dict[str, Any] = {}
for block_name, block_data in blocks.items():
    selected_element = block_data.get(filter_for, "")
    if selected_element is not None and selected_element != "":
        found_elements[selected_element] = found_elements.get(selected_element, 0) + 1

print(f"Found {len(found_elements)} unique elements in the '{filter_for}' field:")
for element in sorted(found_elements):
    print(f"- {element} (appears {found_elements[element]} times)")