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


def beautify_data_structure(original_structure: list | dict) -> dict | list | str | int | float | bool:
    """
    This is a recursive function, designed to unscramble and beautify the mess of the original data.

    :param original_structure: A list or dictionary containing one of the following formats:
        {
            "id": [
                0,
                "button"
            ],              # Here we can also have a deeper list
            ...
        }
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
        ]                   # It is also allowed to have more or less than one entry
        or
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

    :return: Dictionary with the beautified content if given the first format,
        List with the beautified content if given the second format
        String if given the third format,
        Integer or Float if given the fourth format,
        Boolean if given the fifth format,
    """

    if original_structure[0] == 0:
        content: dict | str | int = original_structure[1]

        if type(content) == dict:
            output_dict = {}
            for key in content.keys():
                output_dict[key] = beautify_data_structure(content[key])  # Recursive call
            return output_dict

        elif type(content) == int or type(content) == float:
            return content

        elif content.lower() == "yes":
            return True
        elif content.lower() == "no":
            return False

        else:  # Simple string
            return content

    elif original_structure[0] == 1:  # This means we are using a list
        output_list = []
        for item in original_structure[1]:  # The actual list
            output_list.append(beautify_data_structure(item))  # Recursive call
        return output_list

    else:
        raise NotImplementedError("Decodes of an element value with a depth of more than 1 are not implemented.")


def create_clean_json_file(url: str, filepath: str) -> None:
    """
    This creates a JSON file with all the contents of "entries", but stripped of all the unnecessary numbers in the original data.
    """
    data: dict = get_original_data(url)

    beautified_original_elements: list[dict] = beautify_data_structure(data["entries"])

    new_elements = {}  # A dictionary where the id is the key, and the value is another dictionary with all the data

    for element in beautified_original_elements:
        element_data = {}

        for key in element.keys():
            if key == "id":
                continue
            elif key == "image_url":  # Update the image URL
                element_data[key] = BASE_IMAGE_URL + element["image_url"]
            elif key == "tool" and url == BLOCK_URL:  # Fix the tool in Blocks to use a list instead of comma separated values
                element_data[key] = element['tool'].split(", ")
            else:
                element_data[key] = element[key]

        new_elements[element["id"]] = element_data

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(new_elements, f, indent=4)


if __name__ == "__main__":
    print("Getting mobs...")
    create_clean_json_file(MOB_URL, 'mobs.json')
    print("Getting blocks...")
    create_clean_json_file(BLOCK_URL, 'blocks.json')
    print("Getting items...")
    create_clean_json_file(ITEM_URL, 'items.json')
