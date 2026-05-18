import requests
from bs4 import BeautifulSoup


BASE_URL = "https://minecraft.wiki"


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

    print("Website loaded successfully via MediaWiki API.")
    return html


def list_of_dict_from_table(html: str, wanted_table_number=0) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")

    table = soup.find_all("table", class_="wikitable")[wanted_table_number]

    # Remove all sup and sub of the whole table
    for t in table.find_all(["sup", "sub"]):
        t.decompose()

    table_body = table.find("tbody")
    rows = table_body.find_all("tr")

    # Extract dictionary keys
    key_row = rows[0]
    all_keys = []
    for key in key_row.find_all("th"):
        all_keys.append(key.text.lower().strip())

    output: list[dict[str, str]] = []

    for row in rows[1:]:
        dictionary = {}
        for i, field in enumerate(row.find_all("td")):
            dictionary[all_keys[i]] = field.text.strip()
        output.append(dictionary)

    return output

if __name__ == "__main__":
    _html = get_from_api("List_of_blocks_by_version")
    _output = list_of_dict_from_table(_html)

    print(_output)

    # Now loop through all dictionaries
    _block_html = get_from_api("Grass Block")



