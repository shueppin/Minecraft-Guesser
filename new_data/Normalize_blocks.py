import json
from pathlib import Path
import time
from typing import Any


def normalize_blocks() -> None:
    input_path = Path(__file__).resolve().parent / "blocks.json"
    output_path = Path(__file__).resolve().parent / "blocks_normalized.json"

    with input_path.open("r", encoding="utf-8") as f:
        blocks = json.load(f)

    normalized_blocks = {}
    i : int = 0
    for block_name, block_data in blocks.items():
        normalized_name = block_name.strip().lower().replace(" ", "_")
        new_block_data : dict[str, Any] = {}
        new_block_data["image"] = __new_block_value(block_data, "Image")
        new_block_data["version"] = __new_block_value(block_data, "Version")
        new_block_data["name"] = __as_string(__new_block_value(block_data, "Name"))
        new_block_data["renewable"] = __as_boolean(__new_block_value(block_data, "Renewable"))
        new_block_data["stackable"] = __as_int(__new_block_value(block_data, "Stackable"))
        new_block_data["tool"] = __as_string(__new_block_value(block_data, "tool"))
        new_block_data["blast resistance"] = __as_float(__new_block_value(block_data, "Blast resistance"))
        new_block_data["hardness"] = __as_float(__new_block_value(block_data, "Hardness"))
        new_block_data["luminous"] = __as_boolean(__new_block_value(block_data, "Luminous"))
        new_block_data["transparent"] = __as_string(__new_block_value(block_data, "Transparent"))
        new_block_data["flammable"] = __as_boolean(__new_block_value(block_data, "Flammable"))
        new_block_data["map_color"] = __as_string(__new_block_value(block_data, "Map_color"))

        normalized_blocks[normalized_name] = new_block_data
        print(f"Normalized block {i + 1}/{len(blocks)}: {block_name} -> {normalized_name}")
        i += 1
        time.sleep(0.05) # Sleep so it looks cooler (-;

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(normalized_blocks, f, indent=1)

    print(f"Normalized blocks saved to: {output_path}")


def __new_block_value(block_data : dict, value : str = "") -> str:
    output : str = block_data.get(value, "")
    if output is None:
        return ""
    elif output == None:
        return ""
    return str(output)


def __as_boolean(value : str) -> bool:
    if value.lower() == "yes":
        return True
    elif value.lower() == "no":
        return False
    else:
        return False
    
def __as_float(value : str) -> float:
    try:
        return float(value)
    except ValueError:
        return 0.0
    
def __as_int(value : str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0
    
def __as_string(value : str) -> str:
    return value.strip().lower()


if __name__ == "__main__":
    normalize_blocks()

