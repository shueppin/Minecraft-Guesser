import json
from pathlib import Path
from typing import Any
import re

from normalization_helper import DataParser, clean_text


INPUT_PATH = Path(__file__).resolve().parent / "blocks_raw.json"
OUTPUT_PATH = Path(__file__).resolve().parent / ".." / "data" / "blocks.json"


REMOVED_BLOCKS = [
    "Air",
    "Water",
    "Lava",
    "Nether Portal",
    "End portal",
    "End Gateway",
    "Carrot",
    "Potato",
    "Beetroot",
    "Pitcher Pod",
    "Melon Seeds",
    "Wheat Seeds",
    "Pumpkin Seeds",
    "Torchflower Seeds",
    "Frosted Ice",
    "Piston/Technical components",
    "Bubble Column",
    "Allium",
    "Azure Bluet",
    "Blue Orchid",
    "Cornflower",
    "Lily of the Valley",
    "Oxeye Daisy",
    "Lilac",
    "Peony",
    "Large Fern",
    "Short Grass",
    "Short Dry Grass",
    "Tall Grass",
    "Tall Dry Grass"
]


FIXED_RENEWABLE_VALUES = {
    'Deepslate variant: No\nAll others: Yes': "Partial",
    'No (except via ominous vault)': True,  # Heavy Core
    'No (except via vault)': True,  # Block of Diamond, Jukebox, Enchanting Table
    'Non Warden-Summoning: Yes\nWarden-Summoning: No': True,  # Sculk Shrieker
    'Only bricks: Yes\nWith pottery sherd(s): No': True,  # Decorated Pot
}

TOOL_VALUES = ["Any", "None", "Axe", "Brush", "Bucket", "Hoe", "Pickaxe", "Shears", "Shovel", "Sword"]

LUMINOUS_VALUES = {
    '0': False,
    'Charge 1, 2, 3, 4: Yes (3, 7, 11, 15)\nNot Charged: No': "Depends",
    'Depends on contained liquid': "Depends",
    'JE: Yes (1)\nBE: No': True,
    'No': False,
    'None': False,
    'Small: Yes (1)\nMedium: Yes (2)\nLarge: Yes (4)\nCluster: Yes (5)': True,
    'With a candle:\nYes (3) when lit\nOtherwise: No': "Depends",
    'Yes \n Active or ejecting: 12 \n Inactive: 6': True,
    'Yes (1)': True,
    'Yes (10)': True,
    'Yes (10) when lit': "Depends",
    'Yes (13) (when active)': "Depends",
    'Yes (14)': True,
    'Yes (14) (with berries)': "Depends",
    'Yes (15)': True,
    'Yes (15) (when lit)': "Depends",
    'Yes (15) when lit': "Depends",
    'Yes (2)\nNo (snowlogged)': True,
    'Yes (3)': True,
    'Yes (6)': True,
    'Yes (7)': True,
    'Yes (7) (when lit)': "Depends",
    'Yes (9) (when lit)': "Depends",
    'Yes, when lit \n 1 candle: 3 \n 2 candles: 6 \n 3 candles: 9 \n 4 candles: 12': "Depends",
    'Yes, when lit \n Unoxidized: 15 \n Exposed: 12 \n Weathered: 8 \n Oxidized: 4': "Depends",
    'Yes, when not inactive\nWaiting for players: 4\nActive: 8': "Depends",
    'Yes, when waterlogged \n 1 sea pickle: 6 \n 2 sea pickles: 9 \n 3 sea pickles: 12 \n 4 sea pickles: 15': True,
    'Yes\xa0(10)': True
}

FIXED_TRANSPARENT_VALUES = {
    'Double slab: No\n\nSingle slab: Partial (blocks light)\u200c\nPartial (diffuses sky light)\u200c': "Partial",
    'Double slab: No\n\nSingle slab: Partial (blocks light)\u200c\nYes\u200c': "Partial"
}

FIXED_FLAMMABLE_VALUES = hardcoded_values = {
    'Bamboo: Yes (60)\nShoot: No': "Partial",
    'No\n(burns indefinitely when manually ignited, top side only)': True,
    'No, but burns indefinitely on the top side as soul fire': True,
    'No, but burns indefinitely on the top surface': True,
    'No, but burns indefinitely when manually ignited on the top side only, creating soul fire': True,
    'Yes (JE: 60, BE & edu: 30)': True,
    'Yes (JE: 60, BE: 30)': True,
}

FIXED_FIRE_CATCH_VALUES = {
    'JE: Yes, except  Crimson and  Warped Sign\nBE: Yes': "Partial",
    'Only in Java Edition': True,
    # The following are for things like hanging signs and shelves
    'Yes\n  JE: No\nBE: Yes': "Partial",
    'Yes\n  No': "Partial",
    'Yes\u200c\nNo\u200c': "Partial"
}


def extract_map_color(text: str) -> str:
    """Extract normalized map color token from mixed map color text.

    Rules:
    - Ignore edition markers (JE/BE/...)
    - Prefer COLOR_* tokens when present
    - Otherwise return first meaningful uppercase color-like token
    """
    cleaned = clean_text(text)
    upper = cleaned.upper()

    upper = re.sub(r"\bCOLOR\s+_\s*([A-Z]+)\b", r"COLOR_\1", upper)
    upper = re.sub(r"\bCOLOR\s+([A-Z]+)\b", r"COLOR_\1", upper)

    tokens = re.findall(r"[A-Z_]+", upper)
    stop_words = {
        "JE",
        "BE",
        "JAVA",
        "BEDROCK",
        "EDITION",
        "BLOCK",
        "ITEM",
        "FOLIAGE",
        "TINT",
    }

    for index, token in enumerate(tokens):
        if token in stop_words:
            continue

        if token == "COLOR" and index + 1 < len(tokens):
            next_token = tokens[index + 1].lstrip("_")
            if next_token and next_token not in stop_words:
                return f"COLOR_{next_token}"

        if token.startswith("COLOR_"):
            return token

        if token.isalpha() and token not in stop_words:
            return token

    return ""


def normalize_blocks() -> None:
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        blocks = json.load(f)

    normalized_blocks = {}

    for block_name in sorted(blocks.keys()):
        if block_name in REMOVED_BLOCKS:
            continue

        block_data = blocks[block_name]
        normalized_name = block_name.strip().lower().replace(" ", "_")

        p = DataParser(block_data)

        try:
            new_block_data : dict[str, Any] = {
                "name": block_name,
                "image_url": p.get_raw("image"),

                "blast_resistance": p.extract_first_number("blast resistance"),
                "flammable": p.extract_first_yes_no_partial("flammable", hardcoded_values_dict=FIXED_FLAMMABLE_VALUES),
                "fire_catch": p.extract_first_yes_no_partial("catches fire from lava", hardcoded_values_dict=FIXED_FIRE_CATCH_VALUES),
                "hardness": p.extract_first_number("hardness"),
                "initial_release": p.get_raw("version"),
                "luminous": LUMINOUS_VALUES[p.get_raw("luminous")],
                "renewable": p.extract_first_yes_no_partial("renewable", hardcoded_values_dict=FIXED_RENEWABLE_VALUES),
                "stackable": p.extract_stack_size("stackable"),
                "tool": p.extract_all_from_word_list("tool", word_list=TOOL_VALUES) or p.extract_all_from_word_list("tools", word_list=TOOL_VALUES),
                "transparent": p.extract_first_yes_no_partial("transparent", hardcoded_values_dict=FIXED_TRANSPARENT_VALUES),
                "map_color": extract_map_color(p.get_raw("map color")),
            }
        except KeyError as e:
            print(f'Key Error occurred for "{block_name}" with data: {block_data}')
            return

        normalized_blocks[normalized_name] = new_block_data

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized_blocks, f, indent=4)

    print(f"Normalized blocks saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    normalize_blocks()

