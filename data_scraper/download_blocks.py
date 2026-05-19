from typing import Any
import logging
import tqdm
import json
import os
from pathlib import Path

from download_helper import get_from_api, list_of_dict_from_table, dict_from_infobox, resolve_existing_elements_with_versions_from_list_of_dict


OUTPUT_FILE = Path(__file__).resolve().parent / "blocks_raw.json"
SAVE_EVERY = 20


# Check if the file already exists and is not empty and if you want to overwrite it
if os.path.exists(OUTPUT_FILE) and os.path.getsize(OUTPUT_FILE) > 0:
    if input('The file already exists. Write "yes" to overwrite it: ').lower() != 'yes':
        print("Exiting...")
        exit()


# Get the available blocks
table_html, _ = get_from_api("List_of_blocks_by_version")
table_data = list_of_dict_from_table(table_html)

# Check which blocks exist and resolve their versions
existing_blocks, all_versions_resolved = resolve_existing_elements_with_versions_from_list_of_dict(table_data, "block")

if not all_versions_resolved:
    print("Could not resolve all versions. Not resuming the block download.")
    exit()

# Go through all existing blocks with their version and process them
blocks: dict[str, dict[str, Any]] = {}
processed_count = 0
progress_bar = tqdm.tqdm(total=len(existing_blocks.keys()))

for block_name, version in existing_blocks.items():
    try:
        block_html, redirected_page = get_from_api(block_name)

        if not block_html:
            logging.warning(f"Could not get data for {block_name}")

        # If it was redirected then store the data under the redirected name
        if redirected_page:
            if redirected_page in blocks:
                logging.info(f'Skipping block "{block_name}" as it was redirected to "{redirected_page}" and this already exists')
                progress_bar.update(1)
                continue
            block_name = redirected_page  # Change the name

        if block_name in blocks:
            logging.warning(f'Skipping block "{block_name}" as it already exists')
            continue

        # Get and store the block data and the version
        block_data = dict_from_infobox(block_html)
        blocks[block_name] = block_data
        blocks[block_name]["version"] = version

        # Update the progress and store every so often
        processed_count += 1
        progress_bar.update(1)

        if processed_count % SAVE_EVERY == 0:
            with open(OUTPUT_FILE, "w") as f:
                json.dump(blocks, f, indent=4)


    except Exception as e:
        logging.error(f'Error processing "{block_name}": {e}')

with open(OUTPUT_FILE, "w") as f:
    json.dump(blocks, f, indent=4)
