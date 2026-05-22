import json
from pathlib import Path
from typing import Any

from normalization_helper import DataParser, get_java_edition_part, extract_first_number


actual_dir = Path(__file__).resolve().parent
INPUT_PATH = (actual_dir / ".." / "json_files" / "mobs_raw.json").resolve()
OUTPUT_PATH = (actual_dir / ".." / ".." / "data" / "mobs.json").resolve()


BEHAVIOUR_VALUES = ["Passive", "Neutral", "Hostile"]

CLASSIFICATION_VALUES = ['Animal', 'Animal-adjacent', 'Aquatic', 'Arthropod', 'Illager', 'Monster', 'Undead']


def extract_spawn_and_biomes(text: str, mob_name: str) -> tuple[list[str], list[str]]:
    """
    This extracts the spawning and the biomes where a mob spawns.
    It first returns a sorted list of all the spawning possibilities and then returns a list of all the biomes
    """
    spawn = set()
    biomes = set()

    # Some hardcoded mobs
    if mob_name == "Wandering Trader" or mob_name == "Trader Llama":
        return ["Overworld"], []
    if mob_name == "Ender Dragon":
        return ["Boss", "Player action"], ["The End"]
    if mob_name == "Glow Squid":
        return ["Light level", "Overworld"], []
    if mob_name == "Mule":
        spawn.add("Player action")  # Breeding through the player
    if mob_name == "Sheep" or mob_name == "Pig" or mob_name == "Cow":
        spawn.add("Structure")  # In villages

    lines = text.splitlines()

    # Don't change the order of these
    spawning_decode_dict = {
        "egg": "Hatching",
        "frogspawn": "Hatching",
        "lightning": "Lightning",
        "summoned": "Summoning",
        "reinforcement": "Reinforcement",
        "villager": "Conversion",
        "village": "Structure",
        "built": "Player action",
        "commands": "Commands",
        "jockey": "Jockey",
        "grass": "Grass",
        "light level": "Light level",
        "block": "Block",
        "effect": "Effect",
        "ender pearl": "Ender Pearl",
        "shearing": "Player action",
        "creaking": "Block",
        "bee nests": "Block",
        "nether portal": "Block",
        "spawner": "Spawner",
        "bastion": "Structure",
        "fortress": "Structure",
        "pillager outpost": "Structure",
        "ocean ruins": "Structure",
        "swamp hut": "Structure",
        "end city": "Structure",
        "igloo": "Structure",
        "ocean monument": "Structure",
        "night": "Light level",
        "patrols": "Raiding",
        "raids": "Raiding",
        "thunderstorms": "Lightning",
        "slime chunks": "Overworld",
        "dried ghast": "Block",
        "drowns": "Conversion",
        "siege": "Raiding",
        "sculk": "Block",
        "player": "Player action",
        "horse trap": "Summoning",
        "when": "Conversion",  # Thinks like growing up or being in a dimension too long

        # The following are elements which should be ignored because they are filler lines
        "charged": "",
        "spawning": "",
        "breed": "",
        "regular": "",
        "wandering trader": "",
        "wither": "",
        "overworld": "",
    }

    # Go through all lines individually
    for line in lines:
        # Skip meaningless lines
        if line == "":
            continue

        # Check which keyword occurs. If none occurs, then it is a biome
        for key in spawning_decode_dict:
            if key in line.lower():
                spawn.add(spawning_decode_dict[key])
                break
        else:  # Only run when the for loop quit normally
            biomes.add(line)

    # Remove the filler lines
    spawn.discard("")

    if len(biomes) > 0:
        spawn.add("Biome")

    if len(spawn) == 0:
        spawn.add("Unknown")

    return sorted(list(spawn)), sorted(list(biomes))


def extract_health(text: str) -> int:
    java_edition_text = get_java_edition_part(text)
    return int(extract_first_number(java_edition_text))


def extract_height(text: str, mob_name: str) -> float:
    if mob_name == "Illusioner":  # This is not existent on the wiki
        return 1.95
    return extract_first_number(text)


def normalize_mobs():
    with INPUT_PATH.open("r", encoding="utf-8") as f:
        mobs = json.load(f)

    normalized_mobs = {}

    for raw_mob_name in sorted(mobs.keys()):
        mob_data = mobs[raw_mob_name]
        normalized_name = raw_mob_name.strip().lower().replace(" ", "_")

        p = DataParser(mob_data)

        spawning, biomes = extract_spawn_and_biomes(p.get_raw("spawn"), raw_mob_name)

        try:
            new_mob_data : dict[str, Any] = {
                "name": raw_mob_name,
                "image_url": p.get_raw("image"),
                "initial_release": p.get_raw("version"),

                "behavior": p.extract_all_from_word_list("behavior", word_list=BEHAVIOUR_VALUES),
                "health": extract_health(p.get_raw("health points")),
                "height": extract_height(p.get_raw("hitbox size"), raw_mob_name),
                "classification": p.extract_all_from_word_list("mob type", word_list=CLASSIFICATION_VALUES, unknown_value="Other"),
                "spawn": spawning,
                "biomes": biomes,
            }
        except KeyError as e:
            print(f'Key Error occurred for "{raw_mob_name}" with data: {mob_data}')
            return

        normalized_mobs[normalized_name] = new_mob_data

    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(normalized_mobs, f, indent=4)

    print(f"Saved {len(normalized_mobs.keys())} normalized mobs to: {OUTPUT_PATH}")


if __name__ == "__main__":
    normalize_mobs()
