import json
from pathlib import Path


actual_dir = Path(__file__).resolve().parent
JSON_DIR = actual_dir / "json_files"


def show_all_raw_values(filename: str):
    file_path = JSON_DIR / filename

    with open(file_path) as f:
        raw_data = json.load(f)

    # Create a list of all keys of all elements
    all_keys = set()

    for name, data in raw_data.items():
        all_keys.update(data.keys())

    # Create empty sets for all keys
    all_values_per_key = {}
    for key in all_keys:
        all_values_per_key[key] = set()

    # Go through all elements again and add all available values to the corresponding key
    for name, data in raw_data.items():
        for key in data.keys():
            value = data[key]
            all_values_per_key[key].add(value)

            # To check individual parameters and where they come from
            #if key == "luminance" and value == "No":
                #print(name)

    # Output them all
    for key in sorted(all_values_per_key.keys()):
        print(f"\n{key}: {sorted(all_values_per_key[key])}")

if __name__ == '__main__':
    _filename = input('Enter the filename ("blocks_raw.json", "items_raw.json", "mobs_raw.json"): ')
    show_all_raw_values(_filename)
