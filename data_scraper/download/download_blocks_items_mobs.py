from typing import Any
import logging
import tqdm
import json
import os
from pathlib import Path

from data_scraper.cleanup_text import remove_problem_chars
from download_helper import get_from_api, list_of_dict_from_table, dict_from_infobox, resolve_existing_elements_with_versions_from_list_of_dict, dict_from_table_of_contents


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")

actual_dir = Path(__file__).resolve().parent
OUTPUT_DIR = (actual_dir / ".." / "json_files").resolve()

SAVE_EVERY = 20


def download_all_elements_from_table(output_file_name: str, table_page_title: str, table_name_key: str, element_table_of_contents_keys: list=None, additional_elements: dict[str, str]=None) -> None:
    """
    First opens the List with all the elements and the version, then gets the data of every individual element. Finally stores this data in a file.

    :param output_file_name: File name, including ".json", of the output
    :param table_page_title: Title of the table of the page where the table with all the elements and versions can be found. Example: https://minecraft.wiki/w/List_of_mobs_by_version
    :param table_name_key: Key of the first column of the table (like "blocks", "items", ...)
    :param element_table_of_contents_keys: Keys that should be extracted from the table of contents from each individual element (like "Obtaining", "History", ...)
    :param additional_elements: Additional elements that should be added to the table. It is a dictionary, with the key being the wiki page title and the value the resolved version.
    """

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

    # Add additional elements
    if additional_elements:
        existing_elements.update(additional_elements)

    # Go through all existing elements with their version and process them
    elements_dict: dict[str, dict[str, Any]] = {}
    processed_count = 0
    progress_bar = tqdm.tqdm(total=len(existing_elements.keys()))

    for name, version in existing_elements.items():
        name = remove_problem_chars(name)
        try:
            html, redirected_page = get_from_api(name)

            if not html:
                logger.warning(f'"Could not get data for "{name}"')

            # If it was redirected then store the data under the redirected name
            if redirected_page:
                if redirected_page in elements_dict:
                    logger.info(f'Skipping "{name}" as it was redirected to "{redirected_page}" and this already exists')
                    progress_bar.update(1)
                    continue
                name = redirected_page  # Change the name

            # Remove the underscores from the name to have consistency
            name = name.replace("_", " ")

            if name in elements_dict:
                logger.warning(f'Skipping "{name}" as it already exists')
                progress_bar.update(1)
                continue

            # Get and store the data and the version
            infobox_data = dict_from_infobox(html, identification=name)
            elements_dict[name] = infobox_data
            elements_dict[name]["version"] = version

            # If needed, go through the table of contents too
            if element_table_of_contents_keys:
                table_of_contents_data = dict_from_table_of_contents(html, identification=name, keys=element_table_of_contents_keys)

                for key in table_of_contents_data:
                    # These use the prefix "toc" for "Table of contents"
                    elements_dict[name][f"toc {key.lower()}"] = "\n".join(table_of_contents_data[key].keys())  # We join the individual elements, because our raw data values are supposed to be strings

            # Update the progress and store every so often
            processed_count += 1
            progress_bar.update(1)

            if processed_count % SAVE_EVERY == 0:
                with open(output_file_path, "w") as f:
                    json.dump(elements_dict, f, indent=4)

        except Exception as e:
            logger.error(f'Error processing "{name}": {type(e)} {e}')

    with open(output_file_path, "w") as f:
        json.dump(elements_dict, f, indent=4)


if __name__ == '__main__':
    print("\n\nDownloading blocks...")
    download_all_elements_from_table("blocks_raw.json", "List_of_blocks_by_version", "block", additional_elements={"Light_(block)": "1.17"})

    print("\n\nDownloading items...")
    download_all_elements_from_table("items_raw.json", "List_of_items_by_version", "item", ["Obtaining"], {"Redstone_Dust": "Alpha 1.0.1", "Armor_Stand": "1.8"})

    print("\n\nDownloading mobs...")
    download_all_elements_from_table("mobs_raw.json", "List_of_mobs_by_version", "mob")
