import logging

import requests
from bs4 import BeautifulSoup
import re


BASE_URL = "https://minecraft.wiki"


def _expand_and_clean_url(url: str) -> str:
    url = BASE_URL + url
    url = re.sub(r'[?#].*$', '', url)  # Remove the query at the end
    return url


def get_from_api(page_title: str) -> str:
    # Call API
    api_url = "https://minecraft.wiki/api.php"
    params = {
        "action": "parse",
        "page": page_title,
        "prop": "text",
        "format": "json",
        "formatversion": "2",
    }
    api_response = requests.get(api_url, params=params, timeout=20)
    api_response.raise_for_status()
    payload = api_response.json()
    html: str = payload.get("parse", {}).get("text", "")

    if not html:
        print("API request succeeded but no HTML was returned.")
        return ""

    return html


def list_of_dict_from_table(html: str, wanted_table_number=0) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find_all("table", class_="wikitable")[wanted_table_number]

    # Remove all sup and sub of the whole table
    for element in table.find_all(["sup", "sub"]):
        element.decompose()

    table_body = table.find("tbody")
    rows = table_body.find_all("tr")

    # Extract dictionary keys
    key_row = rows[0]
    all_keys = []
    for key in key_row.find_all("th"):
        all_keys.append(key.text.lower().strip())

    output: list[dict[str, str]] = []

    # Go through all rows of the table
    for row in rows[1:]:
        dictionary = {}
        for i, field in enumerate(row.find_all("td")):
            dictionary[all_keys[i]] = field.text.strip()
        output.append(dictionary)

    return output


def dict_from_infobox(html: str) -> dict[str, str]:
    """
    Takes HTML of an item / block / mob / structure / ... as input

    :return: Returns a dictionary containing the key "image" with the value the URL, if it exists.
    Then, all elements of the infobox are key value pairs, with the key lowercase and the value as string.
    If any elements in the infobox is only an image and no text, then return the src of this image.
    """

    output = {}

    soup = BeautifulSoup(html, "html.parser")

    infobox = soup.find("div", class_="infobox")

    # Remove all sup and sub of the whole table
    for element in infobox.find_all(["sup", "sub"]):
        element.decompose()

    # Get the image
    image_container = infobox.find("span", {"typeof": "mw:File"})  # First image
    if image_container:
        image = image_container.find("img")
        image_url = _expand_and_clean_url(image.get("src"))
        output['image'] = image_url

    # Get all other values of the table
    table = soup.find("table", class_="infobox-rows")

    for row in table.find_all("tr"):
        key = row.find("th").text.lower().strip()
        value_field = row.find("td")

        if not value_field:
            logging.warning(f"No value found for {key}. You can ignore this if the infobox contains subtitles (like biomes do).")
            continue

        # Prefer text if there is text, otherwise if there is an image use the src of the image
        if value_field.text.strip():
            # Replace all br with \n so we can just extract the text
            for br in value_field.find_all("br"):
                br.replace_with("\n")

            value = value_field.text.strip()

        elif value_field.find("img"):
            value = _expand_and_clean_url(value_field.find("img").get("src"))

        else:
            logging.warning(f"Could not decode a value for {key}")
            value = ""

        output[key] = value

    return output

if __name__ == "__main__":
    # This is how to get the data from a table of exactly this style
    _html = get_from_api("List_of_blocks_by_version")
    _output = list_of_dict_from_table(_html)

    print(_output)
    print('\n')

    # Now you would loop through all dictionaries
    # Here we just use some test values
    for _name in ["Grass Block", "Stone", "Allay", "Ancient City", "Mushroom Fields"]:
        _html = get_from_api(_name)
        _output = dict_from_infobox(_html)

        print(f"Name: {_name} \nData: {_output} \n")
