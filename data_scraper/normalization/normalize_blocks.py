import json
import logging
from pathlib import Path
from typing import Any
import re

from data_scraper.cleanup_text import remove_problem_chars
from normalization_helper import DataParser, get_java_edition_part, extract_first_number


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")


actual_dir = Path(__file__).resolve().parent
INPUT_PATH = (actual_dir / ".." / "json_files" / "blocks_raw.json").resolve()
OUTPUT_PATH = (actual_dir / ".." / ".." / "data" / "blocks.json").resolve()


REMOVED_BLOCKS = [
    "Light",
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


HARDCODED_IMAGE_OVERWRITES = {
    "Amethyst Cluster": "https://minecraft.wiki/images/Amethyst_Cluster_%28U%29_JE1_BE2.png",
    "Eyeblossom": "https://minecraft.wiki/images/Open_Eyeblossom_JE1_BE1.png",
    "Ladder": "https://minecraft.wiki/images/Ladder_%28texture%29_JE3_BE2.png",
    "Leaf Litter": "https://minecraft.wiki/images/Leaf_Litter_4_%28S%29_JE2_BE2.png",
    "Nether Wart": "https://minecraft.wiki/images/Nether_Wart_Age_3_JE8.png",
    "Pink Petals": "https://minecraft.wiki/images/Pink_Petals_4_%28S%29_JE2.png",
    "Wildflowers": "https://minecraft.wiki/images/Wildflowers_4_%28S%29_JE1.png"
}


FIXED_RENEWABLE_VALUES = {
    'Deepslate variant: No\nAll others: Yes': "Partial",
    'Non Warden-Summoning: Yes\nWarden-Summoning: No': True,  # Sculk Shrieker
    'Only bricks: Yes\nWith pottery sherd(s): No': "Partial",  # Decorated Pot
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
    'Yes\nActive or ejecting: 12\nInactive: 6': True,
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
    'Yes, when lit\n1 candle: 3\n2 candles: 6\n3 candles: 9\n4 candles: 12': "Depends",
    'Yes, when lit\nUnoxidized: 15\nExposed: 12\nWeathered: 8\nOxidized: 4': "Depends",
    'Yes, when not inactive\nWaiting for players: 4\nActive: 8': "Depends",
    'Yes, when waterlogged\n1 sea pickle: 6\n2 sea pickles: 9\n3 sea pickles: 12\n4 sea pickles: 15': True,
}

FIXED_TRANSPARENT_VALUES = {
    'Double slab: No\n\nSingle slab: Partial (blocks light)\nPartial (diffuses sky light)': "Partial",
    'Double slab: No\n\nSingle slab: Partial (blocks light)\nYes': "Partial"
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
    'Yes\nJE: No\nBE: Yes': "Partial",
    'Yes\nNo': "Partial"
}


def extract_map_color(text: str) -> str:
    """Extract normalized map color token from mixed map color text.

    Rules:
    - Ignore edition markers (JE/BE/...)
    - Prefer COLOR_* tokens when present
    - Otherwise return first meaningful uppercase color-like token
    """
    cleaned = remove_problem_chars(text)
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


def extract_stack_size(text: str) -> int:
    java_edition_part = get_java_edition_part(text)
    number = extract_first_number(java_edition_part, default_value=1)
    return int(number)


def normalize_blocks():
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        blocks = json.load(f)

    normalized_blocks = {}

    for raw_block_name in sorted(blocks.keys()):
        if raw_block_name in REMOVED_BLOCKS:
            continue

        block_data = blocks[raw_block_name]
        normalized_name = raw_block_name.strip().lower().replace(" ", "_")

        p = DataParser(block_data)

        # Replace some automatic images with better ones
        if raw_block_name in HARDCODED_IMAGE_OVERWRITES:
            image_url = HARDCODED_IMAGE_OVERWRITES[raw_block_name]
        else:
            image_url = p.get_raw("image")

        try:
            new_block_data : dict[str, Any] = {
                "name": raw_block_name,
                "image_url": image_url,
                "initial_release": p.get_raw("version"),

                "blast_resistance": p.extract_first_number("blast resistance"),
                "fire_catch": p.extract_first_yes_no_partial("catches fire from lava", hardcoded_values_dict=FIXED_FIRE_CATCH_VALUES),
                "flammable": p.extract_first_yes_no_partial("flammable", hardcoded_values_dict=FIXED_FLAMMABLE_VALUES),
                "hardness": p.extract_first_number("hardness"),
                "luminous": LUMINOUS_VALUES[p.get_raw("luminous")],
                "map_color": extract_map_color(p.get_raw("map color")),
                "renewable": p.extract_first_yes_no_partial("renewable", hardcoded_values_dict=FIXED_RENEWABLE_VALUES),
                "stackable": extract_stack_size(p.get_raw("stackable")),
                "tool": p.extract_all_from_word_list("tool", word_list=TOOL_VALUES) or p.extract_all_from_word_list("tools", word_list=TOOL_VALUES),
                "transparent": p.extract_first_yes_no_partial("transparent", hardcoded_values_dict=FIXED_TRANSPARENT_VALUES),
            }
        except KeyError as e:
            logger.error(f'Key Error "{e}" occurred for "{raw_block_name}" with data: "{block_data}"')
            return

        normalized_blocks[normalized_name] = new_block_data

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized_blocks, f, indent=4)

    print(f"Saved {len(normalized_blocks.keys())} normalized blocks to: {OUTPUT_PATH}")


if __name__ == "__main__":
    normalize_blocks()
