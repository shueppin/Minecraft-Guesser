from typing import Any
import logging
import tqdm
import json
import os
from pathlib import Path

from data_scraper.cleanup_text import remove_escaped_chars
from download_helper import get_from_api, list_of_dict_from_table, dict_from_infobox, resolve_existing_elements_with_versions_from_list_of_dict


actual_dir = Path(__file__).resolve().parent
OUTPUT_DIR = (actual_dir / ".." / "json_files").resolve()

SAVE_EVERY = 20


def download_all_elements_from_table(output_file_name: str, table_page_title: str, table_name_key: str):
    output_file_path = OUTPUT_DIR / output_file_name

    # Check if the file already exists and is not empty and if you want to overwrite it
    if os.path.exists(output_file_path) and os.path.getsize(output_file_path) > 0:
        if input(f'The file "{output_file_name}" already exists. Write "yes" to overwrite it: ').lower() != 'yes':
            print("Exiting...")
            return

    # Get the available elements
    table_html, _ = get_from_api(table_page_title)
    table_data = list_of_dict_from_table(table_html)

    # Check which elements exist (or if they were removed) and resolve their versions
    existing_elements, unresolved_versions = resolve_existing_elements_with_versions_from_list_of_dict(table_data, name_key=table_name_key)

    if unresolved_versions:
        print("\nCould not resolve all versions. Not resuming the download.")
        print("You can find a detailed version history at the bottom of https://minecraft.wiki/w/Java_Edition_version_history/Development_versions")
        print("Unresolved versions: \n" + "\n".join(sorted(unresolved_versions)))
        return

    # Go through all existing elements with their version and process them
    elements_dict: dict[str, dict[str, Any]] = {}
    processed_count = 0
    progress_bar = tqdm.tqdm(total=len(existing_elements.keys()))

    for name, version in existing_elements.items():
        name = remove_escaped_chars(name)
        try:
            html, redirected_page = get_from_api(name)

            if not html:
                logging.warning(f'"Could not get data for "{name}"')

            # If it was redirected then store the data under the redirected name
            if redirected_page:
                if redirected_page in elements_dict:
                    logging.info(f'Skipping "{name}" as it was redirected to "{redirected_page}" and this already exists')
                    progress_bar.update(1)
                    continue
                name = redirected_page  # Change the name

            if name in elements_dict:
                logging.warning(f'Skipping "{name}" as it already exists')
                continue

            # Get and store the data and the version
            element_data = dict_from_infobox(html)
            elements_dict[name] = element_data
            elements_dict[name]["version"] = version

            # Update the progress and store every so often
            processed_count += 1
            progress_bar.update(1)

            if processed_count % SAVE_EVERY == 0:
                with open(output_file_path, "w") as f:
                    json.dump(elements_dict, f, indent=4)


        except Exception as e:
            logging.error(f'Error processing "{name}": {e}')

    with open(output_file_path, "w") as f:
        json.dump(elements_dict, f, indent=4)


if __name__ == '__main__':
    print("\n\nDownloading blocks...")
    download_all_elements_from_table("blocks_raw.json", "List_of_blocks_by_version", "block")

    print("\n\nDownloading items...")
    download_all_elements_from_table("items_raw.json", "List_of_items_by_version", "item")

    print("\n\nDownloading mobs...")
    download_all_elements_from_table("mobs_raw.json", "List_of_mobs_by_version", "mob")
