import json
from pathlib import Path

filter_for : str = "Transparent"

# Load blocks.json
blocks_path = Path(__file__).resolve().parent / "blocks_normalized.json"
with blocks_path.open("r", encoding="utf-8") as f:
    blocks = json.load(f)

found_elements = set()
for block_name, block_data in blocks.items():
    selected_element = block_data.get(filter_for, "")
    if selected_element is not None and selected_element != "":
        found_elements.add(selected_element)

print(f"Found {len(found_elements)} unique elements in the '{filter_for}' field:")
for element in sorted(found_elements):
    print(f"- {element}")