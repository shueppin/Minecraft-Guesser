import json
from pathlib import Path


def normalize_blocks() -> None:
    input_path = Path(__file__).resolve().parent / "blocks.json"
    output_path = Path(__file__).resolve().parent / "blocks_normalized.json"

    with input_path.open("r", encoding="utf-8") as f:
        blocks = json.load(f)

    normalized_blocks = {}
    i : int = 0
    for block_name, block_data in blocks.items():
        normalized_name = block_name.strip().lower().replace(" ", "_")
        new_block_data = {}
        new_block_data["Image"] = __new_block_value(block_data, "Image")
        new_block_data["Version"] = __new_block_value(block_data, "Version")
        new_block_data["Name"] = __new_block_value(block_data, "Name")
        new_block_data["Renewable"] = __new_block_value(block_data, "Renewable")
        new_block_data["Stackable"] = __new_block_value(block_data, "Stackable")
        new_block_data["tool"] = __new_block_value(block_data, "tool")
        new_block_data["Blast resistance"] = __new_block_value(block_data, "Blast resistance")
        new_block_data["Hardness"] = __new_block_value(block_data, "Hardness")
        new_block_data["Luminous"] = __new_block_value(block_data, "Luminous")
        new_block_data["Transparent"] = __new_block_value(block_data, "Transparent")
        new_block_data["Flammable"] = __new_block_value(block_data, "Flammable")
        new_block_data["Map_color"] = __new_block_value(block_data, "Map_color")

        normalized_blocks[normalized_name] = new_block_data
        print(f"Normalized block {i + 1}/{len(blocks)}: {block_name} -> {normalized_name}")
        i += 1

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


if __name__ == "__main__":
    normalize_blocks()

