import logging
import json
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

from data_scraper.cleanup_text import remove_problem_chars


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s %(name)s: %(message)s")

actual_dir = Path(__file__).resolve().parent
VERSIONS_JSON_PATH = (actual_dir / ".." / "json_files" / "versions.json").resolve()

BASE_URL = "https://minecraft.wiki"

def _expand_and_clean_url(url: str) -> str:
    url = BASE_URL + url
    url = re.sub(r'[?#].*$', '', url)  # Remove the query at the end
    return url


def get_from_api(page_title: str) -> tuple[str, str | None]:
    """
    Get the HTML page with this title from the API.

    :return: Returns the HTML of the page and if it was redirected, also the page title of the new page. Otherwise, the second argument is empty.
    """

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
        logger.warning(f'API request succeeded but no HTML was returned for page "{page_title}"')
        return "", ""

    # Primitive check to see if it is a redirect
    if "mw:PageProp/redirect" in html:
        soup = BeautifulSoup(html, "html.parser")
        redirect_page_title = soup.find("ul", class_="redirectText").find("a").text.strip()  # Get the redirect URL and again check if it really is a redirect
        redirect_page_title = re.sub(r'#.*$', '', redirect_page_title)  # Shorten it and remove any unnecessary suffixes

        new_html, again_redirected_page = get_from_api(redirect_page_title)

        if again_redirected_page:
            return new_html, again_redirected_page
        else:
            return new_html, redirect_page_title

    return html, ""


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
            # If we are in the first field (element name), try to get the link directly, otherwise use the text
            if i == 0:
                link = field.find("a")
                if link:
                    dictionary[all_keys[i]] = unquote(link.get("href").replace("/w/", "", 1))  # Remove the prefix "/w/"
                else:
                    dictionary[all_keys[i]] = field.text.strip()

            else:
                dictionary[all_keys[i]] = field.text.strip()

        output.append(dictionary)

    return output


def resolve_existing_elements_with_versions_from_list_of_dict(input_list: list[dict[str, str]], name_key: str, added_key="added", removed_key="removed") -> tuple[dict[str, str], set[str]]:
    """
    Given a list of dictionaries, check whether the element (Mob / Item / Block / ...) still exists based on the version history and if so,
    return it with the corresponding minecraft full release version when it was added.

    :param input_list: List of dictionaries. Output from list_of_dict_from_table.
    :param name_key: For each element of the dictionary, this is the key where the name is stored. The name will then be used in the output as key. Example: "block", "item", "mob", ...
    :param added_key: For each element of the dictionary, this is the key where the minecraft version when this element was added is stored.
    :param removed_key: For each element of the dictionary, this is the key where the minecraft version when this element was removed is stored.
    :return: Dictionary with the name as the key and the minecraft full release version as the value. Also returns a list of all unresolved versions.
    """

    with open(VERSIONS_JSON_PATH) as f:
        version_resolver = json.load(f)

    unresolved_versions = set()
    output = {}

    for dictionary in input_list:
        name = dictionary[name_key]
        added_dates = dictionary[added_key].split(", ")  # Split these
        removed_dates = dictionary[removed_key].split(", ")

        if "-" in removed_dates:
            removed_dates.remove("-")  # Cleanup this element

        # Check if it was as many times removed as it was added and if so, it does not exist anymore. This is a primitive existence checker.
        if len(removed_dates) >= len(added_dates):
            logger.info(f"{name} was completely removed.")
            continue

        # Get the full version in which it was added
        if added_dates[-1] in version_resolver:
            version = version_resolver[added_dates[-1]]
        else:
            logger.warning(f'Version "{added_dates[-1]}" was not found in the database')
            unresolved_versions.add(added_dates[-1])
            continue

        output[name] = version

    return output, unresolved_versions


def dict_from_infobox(html: str, identification: str) -> dict[str, str]:
    """
    Takes HTML of an item / block / mob / structure / ... as input.
    Identification is only used for debugging purposes.

    :return: Returns a dictionary containing the key "image" with the value the URL, if it exists.
    Then, all elements of the infobox are key value pairs, with the key lowercase and the value as string.
    If any elements in the infobox is only an image and no text, then return the src of this image.
    """

    output = {}

    soup = BeautifulSoup(html, "html.parser")

    infobox = soup.find("div", class_="infobox")

    if not infobox:
        logger.warning(f'For element "{identification}", Infobox was not found')
        return output

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
        # Replace all br with \n so we can just extract the text
        for br in row.find_all("br"):
            br.replace_with("\n")

        key = row.find("th").text.lower().strip()
        key = remove_problem_chars(key.replace("\n", " "))
        value_field = row.find("td")

        if not value_field:
            # Ignore this, because these are probably just subtitles, for example in biomes
            continue

        # Prefer text if there is text, otherwise if there is an image use the src of the image
        if value_field.text.strip():
            value = remove_problem_chars(value_field.text)

        elif value_field.find("img"):  # If there is at least one image, then go through all of them
            all_img_src = []
            for img in value_field.find_all("img"):
                all_img_src.append(_expand_and_clean_url(img.get("src")))

            value = remove_problem_chars("\n".join(all_img_src))

        else:
            logger.warning(f'Could not decode a value for element "{identification}" with key "{key}"')
            value = ""

        output[key] = value

    return output


def dict_from_table_of_contents(html: str, identification: str, keys: list=None) -> dict[str, dict[str, ...] | list[str]]:
    """
    Returns a dictionary from the HTML with the table of contents.
    If the keys are None, then the whole table is returned, otherwise just the data of the given keys, including the key.
    Identification is only used for debugging purposes.
    """

    # Helper function
    def parse_outline(text):
        """
        Parse a numbered outline (1, 1.1, 1.1.1, ...) into a nested dict
        where keys are headings (numbers removed) and values are nested dicts.
        """
        root = {}
        stack = [(0, root)]  # (level, dict_for_that_level)
        line_re = re.compile(r'^\s*([\d.]+)\s+(.*\S)\s*$')

        for raw in text.splitlines():
            m = line_re.match(raw)
            if not m:
                continue
            num, title = m.group(1), m.group(2)
            level = num.count('.') + 1  # "1" -> 1, "1.1" -> 2, etc.
            # Create node
            node = {}
            # Find parent for this level
            while stack and stack[-1][0] >= level:
                stack.pop()
            parent = stack[-1][1]
            parent[title] = node
            stack.append((level, node))

        return root

    # Initial value
    if keys is None:
        keys = []

    # Extract the text
    soup = BeautifulSoup(html, "html.parser")

    table_of_contents = soup.find("div", id="toc")
    contents_text = table_of_contents.text.strip("Contents").strip()
    contents_text = remove_problem_chars(contents_text)

    contents_dict: dict[str, dict[str, ...]] = parse_outline(contents_text)

    # Output either the whole dict or just the given keys
    if keys:
        output = {}
        for key in keys:
            if key not in contents_dict:
                logger.warning(f'Could not find key "{key}" for element "{identification}" in "{contents_dict}"')
                continue
            output[key] = contents_dict[key]

        return output

    return contents_dict


if __name__ == "__main__":
    # This is how to get the data from a table of exactly this style
    _html, _ = get_from_api("List_of_blocks_by_version")
    _output = list_of_dict_from_table(_html)

    print(_output)
    print('\n')

    # Now you would loop through all dictionaries
    # Here we just use some test values
    for _name in ["Grass Block", "Stone", "Allay", "Ancient City", "Mushroom Fields", "Red Bed", "Bamboo", "Light"]:
        _html, _redirected_page = get_from_api(_name)
        _output = dict_from_infobox(_html, identification=_name)

        _redirect_message = f"(redirected to {_redirected_page})" if _redirected_page else ""
        print(f"Name: {_name} {_redirect_message} \nData: {_output} \n")

    # Examples for table of content
    for _name in ["Slimeball", "Sugar"]:
        _html, _redirected_page = get_from_api(_name)
        _output = dict_from_table_of_contents(_html, identification=_name)

        _redirect_message = f"(redirected to {_redirected_page})" if _redirected_page else ""
        print(f"Name: {_name} {_redirect_message} \nTable of contents: \n{_output} \n")
