import json
from pathlib import Path
from typing import Any

from normalization_helper import *


REMOVED_BLOCKS = [
    "Air",
    "Water",
    "Lava",
    "Nether Portal",
    "End portal",
    "Carrot",
    "Potato",
    "Beetroot",
    "End Gateway"
]


# These are all the values that appear in the wiki with a fixed hard-coded value
RENEWABLE_VALUES = {
    'Deepslate variant: No\nAll others: Yes': "Partial",
    'JE: No\nBE: Yes': False,
    'No (except via ominous vault)': True,  # Heavy Core
    'No (except via vault)': True,  # Block of Diamond, Jukebox, Enchanting Table
    'Non Warden-Summoning: Yes\nWarden-Summoning: No': True,  # Sculk Shrieker
    'No\u200c\nYes\u200c': False,  # Netherrack
    'No': False,
    'Only bricks: Yes\nWith pottery sherd(s): No': True,  # Decorated Pot
    'Yes': True
}

STACKABLE_VALUES = {
    'JE: No\nBE: Yes (64)': 1,
    'No': 1,
    'Yes (16)': 16,
    'Yes (64)': 64,
    'Yes (64) (same species only)': 64,
    'Yes (64) without bees inside\nNo with bee(s) inside': 64,
    'Yes (64), same color only': 64,
    'Yes (64), same damage state only': 64,
    'Yes (64), same type only': 64,
    'Yes (64); same type only': 64,
    'Yes (64)\u200c': 64,
    'Yes (64)\u200c\n\nN/A\u200c': 64,
    'Yes (64)\u200c\nN/A\u200c': 64,
    'Yes\xa0(64)': 64
}

TOOL_VALUES = {
    'Any tool': "Any",
    'None': "None",
    'https://minecraft.wiki/images/Invicon_Diamond_Pickaxe.png': "Pickaxe",
    'https://minecraft.wiki/images/Invicon_Iron_Pickaxe.png': "Pickaxe",
    'https://minecraft.wiki/images/Invicon_Shears.png': "Shears",
    'https://minecraft.wiki/images/Invicon_Stone_Pickaxe.png': "Pickaxe",
    'https://minecraft.wiki/images/Invicon_Wooden_Pickaxe.png': "Pickaxe",
    'https://minecraft.wiki/images/Invicon_Wooden_Shovel.png': "Shovel",
    'https://minecraft.wiki/images/SlotSprite_Axe_Required.png': "Axe",
    'https://minecraft.wiki/images/SlotSprite_Bucket_Required.png': "Bucket",
    'https://minecraft.wiki/images/SlotSprite_Hoe_Required.png': "Hoe",
    'https://minecraft.wiki/images/SlotSprite_Pickaxe_Required.png': "Pickaxe",
    'https://minecraft.wiki/images/SlotSprite_Shovel_Required.png': "Shovel",
    'https://minecraft.wiki/images/Invicon_Brush.png': "Brush",
    'https://minecraft.wiki/images/SlotSprite_Sword_Required.png': "Sword",
}

HARDNESS_VALUES = {
    'Coal Ore: 3\n\nDeepslate Coal Ore: 4.5': 3.0,
    'Copper Ore: 3\n\nDeepslate Copper Ore: 4.5': 3.0,
    'Diamond Ore: 3\n\nDeepslate Diamond Ore: 4.5': 3.0,
    'Emerald Ore: 3\nDeepslate Emerald Ore: 4.5': 3.0,
    'Gold Ore: 3\nDeepslate Gold Ore: 4.5': 3.0,
    'Iron Ore: 3\n\nDeepslate Iron Ore: 4.5': 3.0,
    'Lapis Lazuli Ore: 3\n\nDeepslate Lapis Lazuli Ore: 4.5': 3.0,
    'Redstone Ore: 3\n\nDeepslate Redstone Ore: 4.5': 3.0,
    'Stone and stone bricks: 0.75\n\nCobblestone: 1\n\nDeepslate: 1.5': 0.75
}

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

TRANSPARENT_VALUES = {
    'Double slab: No\n\nSingle slab: Partial (blocks light)\u200c\nPartial (diffuses sky light)\u200c': "Partial",
    'Double slab: No\n\nSingle slab: Partial (blocks light)\u200c\nYes\u200c': "Partial",
    'JE: No\nBE: Yes': False,
    'JE: Partial\nBE: Yes': "Partial",
    'JE: Partial  (diffuses sky light) \nBE: Yes': "Partial",
    'JE: Partial (-1 to light)\nBE: Partial (diffuses sky light, -2 to light)': "Partial",
    'JE: Partial (-1 to light)\nBE: Yes': "Partial",
    'JE: Partial (diffuses sky light)\nBE: Partial (diffuses sky light, -1 to light)': "Partial",
    'JE: Partial (diffuses sky light)\nBE: Yes': "Partial",
    'JE: Yes\nBE: Partial (allows light to pass through)': True,
    'JE: Yes\nBE: Partial (diffuses sky light, -2 to light)': True,
    'Java Edition: No\nBedrock Edition: Yes': False,
    'Java Edition: Partial (Blocks light)\nBedrock Edition: Yes': "Partial",
    'No': False,
    'No (Java Edition)\nYes (Bedrock Edition)': False,
    'Partial': "Partial",
    'Partial (blocks light)': "Partial",
    'Partial (blocks light)\u200c\nYes\u200c': "Partial",
    'Partial (blocks light, mob spawning possible)': "Partial",
    'Partial (diffuses sky light)': "Partial",
    'Partial (does not block light)': "Partial",
    'Partial (lets light pass through)': "Partial",
    'Partial (suffocates mobs, blocks sunlight, blocks beacons)': "Partial",
    'Partial (when active)': "Partial",
    'Partially': "Partial",
    'Yes': True
}

FLAMMABLE_VALUES = {
    '?': "Unknown",
    'Bamboo: Yes (60)\nShoot: No': "Partial",
    'JE: Yes (15)\nBE: No': True,
    'JE: Yes (60)\nBE: No': True,
    'JE: Yes (60)\nBE: Yes (30)': True,
    'No': False,
    'No\n(burns indefinitely when manually ignited, top side only)': True,
    'No, but burns indefinitely on the top side as soul fire': True,
    'No, but burns indefinitely on the top surface': True,
    'No, but burns indefinitely when manually ignited on the top side only, creating soul fire': True,
    'No\u200c\nYes\u200c': False,
    'Yes': True,
    'Yes (15)': True,
    'Yes (30)': True,
    'Yes (30)\n  No': True,
    'Yes (5)': True,
    'Yes (5)\n  No': True,
    'Yes (60)': True,
    'Yes (JE: 60, BE & edu: 30)': True,
    'Yes (JE: 60, BE: 30)': True,
}

FIRE_CATCH_VALUES = {
    'Block: Yes\nItem: No': True,
    'JE: No\nBE: Yes': False,
    'JE: Yes\nBE: No': True,
    'JE: Yes, except  Crimson and  Warped Sign\nBE: Yes': "Partial",
    'No': False,
    'Only in Java Edition': True,
    'Yes': True,
    'Yes\n  JE: No\nBE: Yes': False,
    'Yes\n  No': True,
    'Yes\u200c\nNo\u200c': True
}


def normalize_blocks() -> None:
    input_path = Path(__file__).resolve().parent / "blocks_raw.json"
    output_path = Path(__file__).resolve().parent.parent / "blocks.json"

    with input_path.open("r", encoding="utf-8") as f:
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

                "blast_resistance": p.get_float("blast resistance"),
                "flammable": FLAMMABLE_VALUES[p.get_raw("flammable")],
                "fire_catch": FIRE_CATCH_VALUES[p.get_raw("catches fire from lava")],
                "hardness": p.get_float("hardness", complex_extraction_dict=HARDNESS_VALUES),
                "initial_release": p.get_raw("version"),
                "luminous": LUMINOUS_VALUES[p.get_raw("luminous")],
                "renewable": RENEWABLE_VALUES[p.get_raw("renewable")],
                "stackable": STACKABLE_VALUES[p.get_raw("stackable")],
                "tool": TOOL_VALUES[p.get_raw("tool") or p.get_raw("tools")],
                "transparent": TRANSPARENT_VALUES[p.get_raw("transparent")],
                # Ignored Map color for simplicity
            }
        except KeyError as e:
            print(f'Key Error occurred for "{block_name}" with data: {block_data}')
            return

        normalized_blocks[normalized_name] = new_block_data

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(normalized_blocks, f, indent=4)

    print(f"Normalized blocks saved to: {output_path}")


if __name__ == "__main__":
    normalize_blocks()

