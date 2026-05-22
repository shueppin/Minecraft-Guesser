import json
from pathlib import Path
from typing import Any

from normalization_helper import DataParser, extract_all_from_word_list


actual_dir = Path(__file__).resolve().parent
INPUT_PATH = (actual_dir / ".." / "json_files" / "items_raw.json").resolve()
OUTPUT_PATH = (actual_dir / ".." / ".." / "data" / "items.json").resolve()


REMOVED_ITEMS = [
    "Mundane Potion",
    "Awkward Potion",
    "Thick Potion",
    # Removes all individual potions, pottery sherds and armor trims in the main block.
]


HARDCODED_IMAGE_OVERWRITES = {
    "Beetroot Seeds": "https://minecraft.wiki/images/Beetroot_Seeds_JE3_BE3.png",
    "Melon Seeds": "https://minecraft.wiki/images/Melon_Seeds_JE2_BE2.png",
    "Pumpkin Seeds": "https://minecraft.wiki/images/Pumpkin_Seeds_JE1_BE1.png",
    "Torchflower Seeds": "https://minecraft.wiki/images/Torchflower_Seeds_JE1_BE1.png",
    "Pitcher Pod": "https://minecraft.wiki/images/Pitcher_Pod_JE1_BE1.png",
    "Wheat Seeds": "https://minecraft.wiki/images/Wheat_Seeds_JE1_BE1.png",
    "Carrot": "https://minecraft.wiki/images/Carrot_JE3_BE2.png",
    "Potato": "https://minecraft.wiki/images/Potato_JE3_BE2.png",
    "Glow Berries": "https://minecraft.wiki/images/Glow_Berries_JE1_BE1.png",
    "Kelp": "https://minecraft.wiki/images/Kelp_%28item%29_JE1_BE2.png",
    "Trident": "https://minecraft.wiki/images/Trident_%28item%29_JE2_BE1.png",
    "Turtle Egg": "https://minecraft.wiki/images/Turtle_Egg_%28item%29_JE2_BE2.png",
    "Arrow": "https://minecraft.wiki/images/Arrow_%28item%29_JE1_BE1.png",
    "Spectral Arrow": "https://minecraft.wiki/images/Spectral_Arrow_%28item%29_JE2.png",
    "Wind Charge": "https://minecraft.wiki/images/Wind_Charge_%28item%29_JE1_BE1.png",
    "End Crystal": "https://minecraft.wiki/images/End_Crystal_%28item%29_JE2_BE2.png",
}


RARITY_VALUES = ["Common", "Uncommon", "Rare", "Epic"]

FIXED_RENEWABLE_VALUES = {
    'Buried Treasure: No\nOthers: Yes': "Partial",
    'Luck and Uncraftable , Decay : No\n\nAll others: Yes': True,
    'Luck and Uncraftable : No\n\nAll others: Yes': True,
    'Swift Sneak: No\nWind Burst: No (except via ominous vault)\nAll others: Yes': "Partial",
    'With Trail Effect: No (except via vault)\nWithout Trail Effect: Yes': "Partial",  # Fireworks
}

TEMPORARY_OBTAINING_VALUES = [
    "Bartering",
    "Brewing",
    "Cat gifts",
    "Chest loot",  # Later replaced with "Container loot"
    "Cooking",  # Later replaced with "Smelting"
    "Crafting",
    "Fishing",
    "Generated loot",  # Later replaced with "Container loot"
    "Interacting",  # Later replaced with "Other"
    "Mob loot",
    "Smelting",
    "Trading",
    "Villager gifts"
]


def extract_obtaining(text: str, item_name: str) -> list:
    obtaining_values = set(extract_all_from_word_list(text, word_list=TEMPORARY_OBTAINING_VALUES, unknown_value="None"))

    # Some hardcoded values
    if item_name == "Stick":
        obtaining_values.add("Mob loot")  # It only has entity loot, which is not good
    elif item_name == "Elytra":
        obtaining_values.add("Container loot")
    elif item_name == "Written Book":
        obtaining_values.add("Other")
    elif item_name == "Torchflower Seeds" or item_name == "Pitcher Pod":
        obtaining_values.add("Other")
    elif item_name.startswith("Bucket of"):
        obtaining_values.add("Other")
    elif "Horse Armor" in item_name:
        obtaining_values.add("Container loot")

    # Replace "Chest loot" and "Generated loot" with "Container loot"
    if "Chest loot" in obtaining_values or "Generated loot" in obtaining_values:
        obtaining_values.discard("Chest loot")
        obtaining_values.discard("Generated loot")
        obtaining_values.add("Container loot")

    if "Cooking" in obtaining_values:
        obtaining_values.discard("Cooking")
        obtaining_values.add("Smelting")

    if "Interacting" in obtaining_values:  # For buckets
        obtaining_values.discard("Interacting")
        obtaining_values.add("Other")

    # Remove the default value, in case it was still there
    if len(obtaining_values) > 1:
        obtaining_values.discard("None")

    return sorted(list(obtaining_values))


def extract_drops_from_block(text: str) -> bool:
    if "Breaking" in text or "Farming" in text or "Mining" in text or "Block loot" in text:
        return True
    return False

def normalize_items():
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        items = json.load(f)

    normalized_items = {}

    for raw_item_name in sorted(items.keys()):
        # Remove all unwanted items
        if raw_item_name in REMOVED_ITEMS:
            continue
        if "Potion of" in raw_item_name:
            continue
        if "Pottery Sherd" in raw_item_name:
            continue
        if "Armor Trim" in raw_item_name:
            continue

        item_data = items[raw_item_name]
        normalized_name = raw_item_name.strip().lower().replace(" ", "_")

        p = DataParser(item_data)

        # Replace some automatic images with better ones
        if raw_item_name in HARDCODED_IMAGE_OVERWRITES:
            image_url = HARDCODED_IMAGE_OVERWRITES[raw_item_name]
        else:
            image_url = p.get_raw("image")

        try:
            new_item_data : dict[str, Any] = {
                "name": raw_item_name,
                "image_url": image_url,
                "initial_release": p.get_raw("version"),

                "drops_from_block": extract_drops_from_block(p.get_raw("toc obtaining")),
                "obtaining": extract_obtaining(p.get_raw("toc obtaining"), raw_item_name),
                "rarity": p.extract_first_from_word_list("rarity tier", RARITY_VALUES, unknown_value="Common"),
                "renewable": p.extract_first_yes_no_partial("renewable", hardcoded_values_dict=FIXED_RENEWABLE_VALUES),
                "stackable": p.extract_stack_size("stackable"),
            }
        except KeyError as e:
            print(f'Key Error occurred for "{raw_item_name}" with data: {item_data}')
            return

        normalized_items[normalized_name] = new_item_data

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized_items, f, indent=4)

    print(f"Saved {len(normalized_items.keys())} normalized items to: {OUTPUT_PATH}")


if __name__ == "__main__":
    normalize_items()
