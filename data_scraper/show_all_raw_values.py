import json


INPUT_FILE = "blocks_raw.json"


with open(INPUT_FILE) as f:
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
