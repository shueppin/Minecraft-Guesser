import json
from pathlib import Path


def load_blocks() -> dict:
    """Load data/blocks.json and return as a dictionary."""
    base = Path(__file__).parent
    path = base / "data" / "items.json"
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    blocks = load_blocks()
    
    possible = {}

    for key, data in blocks.items():
        if (
            data["stackable"] == 1 and
            data["renewable"] == True and
            data["drops_from_block"] == False and
            data["rarity"] == "Common" and
            data["initial_release"] == "pre-alpha" and 
            "Container loot" in data["obtaining"] and
            ("Crafting" in data["obtaining"] or "Fishing" in data["obtaining"] or "Mob loot" in data["obtaining"]) and
            not(len(data["obtaining"])== 4 and "Container loot" in data["obtaining"] and "Crafting" in data["obtaining"] and "Mob loot" in data["obtaining"] and "Villager gifts" in data["obtaining"]) and
            not(len(data["obtaining"])== 4 and "Container loot" in data["obtaining"] and "Crafting" in data["obtaining"] and "Trading" in data["obtaining"] and "Villager gifts" in data["obtaining"]) and
            not(len(data["obtaining"])== 4 and "Container loot" in data["obtaining"] and "Crafting" in data["obtaining"] and "Mob loot" in data["obtaining"] and "Trading" in data["obtaining"]) and
            not(len(data["obtaining"])== 2 and "Container loot" in data["obtaining"] and "Crafting" in data["obtaining"]) and
            not(len(data["obtaining"]) == 3 and "Crafting" in data["obtaining"] and "Mob loot" in data["obtaining"] and "Fishing" in data["obtaining"]) and
            not(len(data["obtaining"]) == 5 and "Crafting" in data["obtaining"] and "Mob loot" in data["obtaining"] and "Fishing" in data["obtaining"] and "Container loot" in data["obtaining"] and "Trading" in data["obtaining"]) and
            (len(data["obtaining"]) == 3 and "Crafting" in data["obtaining"] and "Mob loot" in data["obtaining"] and "Container loot" in data["obtaining"])
        ):
            possible[key] = data

    print("Possible blocks:")
    for key in possible:
        print(f"- {key}")

