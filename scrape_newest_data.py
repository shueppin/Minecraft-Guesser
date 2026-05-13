from bs4 import BeautifulSoup
import requests
import json


MOB_URL = 'https://www.mcdle.net/mob'
BLOCK_URL = 'https://www.mcdle.net/block'
ITEM_URL = 'https://www.mcdle.net/item'

BASE_IMAGE_URL = 'https://www.mcdle.net'


def get_original_data(url: str) -> dict:
    response = requests.get(url)
    html = response.content

    soup = BeautifulSoup(html, "html.parser")

    data_container = soup.find("body").find("main").find("div").find("astro-island", recursive=False)  # Find only one occurrence of "astro-island" not all of them inside another div too.
    data = data_container.get("props")

    return json.loads(data)


def discover_element_value_list(element_value_list: list) -> list[str] | str | bool | int | float:
    """
    This is a helper function, designed to unscramble the mess of the original data.
    :param element_value_list: A list containing the value of the actual element of a certain key. This needs to be in the format:
        [
            0,
            "Button"
        ]
        or
        [
            0,
            64
        ]
        or
        [
            0,
            "Yes"
        ]
        or
        [
            1,
            [
                [
                    0,
                    "Structure"
                ],
                [
                    0,
                    "Duplication"
                ]
            ]
        ]
        (it is also allowed to have just one entry)
    :return: String if given the first format, Int or float if given the second format, Boolean if given the third format, List of Strings if given the fourth format
    """
    if element_value_list[0] == 0:
        element_value: str | int = element_value_list[1]
        if type(element_value) == int or type(element_value) == float:
            return element_value
        elif element_value.lower() == "yes":
            return True
        elif element_value.lower() == "no":
            return False
        else:
            return element_value

    elif element_value_list[0] == 1:
        output_list = []
        for item in element_value_list[1]:  # The actual list
            output_list.append(discover_element_value_list(item))  # Recursive call, this should only be called one layer deeper.
        return output_list

    else:
        raise NotImplementedError("Decodes of an element value with a depth of more than 1 are not implemented.")


def create_clean_json_file(url: str, filepath: str) -> None:
    """
    This creates a JSON file with all the contents of "entries", but stripped of all the unnecessary numbers in the original data.
    """
    data: dict = get_original_data(url)

    original_elements: list[list] = data["entries"][1]  # The first element of "entries" is only "1", and the second is a list containing all the entries

    new_elements = {}  # A dictionary where the id is the key, and the value is another dictionary with all the data

    for element in original_elements:
        original_element_dict: dict = element[1]  # Skip the first element, which is only "0"

        minecraft_id = discover_element_value_list(original_element_dict.get("id"))
        entry_data = {}

        for key in original_element_dict.keys():
            if key == "id":
                continue

            if key == "image_url":
                entry_data[key] = BASE_IMAGE_URL + discover_element_value_list(original_element_dict[key])
            else:
                entry_data[key] = discover_element_value_list(original_element_dict[key])

        new_elements[minecraft_id] = entry_data

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_elements, f, indent=4)


if __name__ == "__main__":
    print("Getting mobs...")
    create_clean_json_file(MOB_URL, 'mobs.json')
    print("Getting blocks...")
    create_clean_json_file(BLOCK_URL, 'blocks.json')
    print("Getting items...")
    create_clean_json_file(ITEM_URL, 'items.json')
