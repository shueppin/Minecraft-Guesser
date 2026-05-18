"""Download and extract Minecraft block infobox data from Minecraft Wiki.

This module:
- Reads the Java Edition block list from Download_versions.JavaEditionVersionParser.
- Fetches each block page (following redirect pages when necessary).
- Extracts selected infobox fields into blocks.json.
"""

import json
import re
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urljoin, urlsplit

import Download_versions
import requests  # type: ignore
from bs4 import BeautifulSoup


BASE_URL = "https://minecraft.wiki"
SAVE_EVERY = 10


def _page_title_from_url(url: str) -> str:
    """Return a decoded page title derived from the last URL path segment."""
    path = urlsplit(url).path.rstrip("/")
    title = path.rsplit("/", 1)[-1] if path else ""
    return unquote(title).replace("_", " ")


def _clean_text(value: str) -> str:
    """Normalize whitespace and decode HTML entities."""
    return re.sub(r"\s+", " ", unescape(value)).strip()


def _page_html_from_url(url: str) -> str:
    """Fetch rendered page HTML for a wiki URL through MediaWiki API."""
    parsed = urlsplit(url)
    page_title = unquote(parsed.path.rstrip("/").rsplit("/", 1)[-1]).replace("_", " ")

    api_url = f"{BASE_URL}/api.php"
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
    html = payload.get("parse", {}).get("text", "")

    if not html:
        raise ValueError(f"No HTML returned for {url}")

    return html


def _extract_redirect_url(html: str, current_url: str) -> str | None:
    """Extract redirect target URL from rendered HTML, if the page is a redirect."""
    soup = BeautifulSoup(html, "html.parser")

    redirect_link = soup.select_one('link[rel="mw:PageProp/redirect"]')
    if redirect_link and redirect_link.get("href"):
        href = str(redirect_link.get("href"))
        if href.startswith("#"):
            # Fragment-only redirect (e.g. "#cite_note...") — ignore it.
            return None
        candidate = urljoin(BASE_URL, href)
        # If resolved candidate has no path component, ignore it as malformed.
        if urlsplit(candidate).path in ("", "/"):
            return None
        return candidate

    fallback_anchor = soup.select_one(".redirectText a")
    if fallback_anchor and fallback_anchor.get("href"):
        href = str(fallback_anchor.get("href"))
        if href.startswith("#"):
            return None
        candidate = urljoin(BASE_URL, href)
        if urlsplit(candidate).path in ("", "/"):
            return None
        return candidate

    return None


def _extract_tool_name(td: Any) -> str | None:
    """Return first matching tool keyword from infobox tool cell images/text."""
    tool_names = ["pickaxe", "axe", "hoe", "sword", "shovel"]
    text_parts: list[str] = []

    for img in td.find_all("img"):
        text_parts.extend(
            str(value)
            for value in (
                img.get("alt"),
                img.get("title"),
                img.get("src"),
            )
            if value
        )

    haystack = " ".join(text_parts).lower()
    for tool_name in tool_names:
        if tool_name in haystack:
            return tool_name

    return None


def _extract_stackable_number(text: str) -> int | None:
    """Extract stack size from patterns like 'Yes (64)' -> 64."""
    match = re.search(r"\((\d+)\)", text)
    return int(match.group(1)) if match else None


def _extract_map_color(text: str) -> str | None:
    """Extract normalized map color token from mixed map color text.

    Rules:
    - Ignore edition markers (JE/BE/...)
    - Prefer COLOR_* tokens when present
    - Otherwise return first meaningful uppercase color-like token
    """
    cleaned = _clean_text(text)
    upper = cleaned.upper()

    upper = re.sub(r"\bCOLOR\s+_\s*([A-Z]+)\b", r"COLOR_\1", upper)
    upper = re.sub(r"\bCOLOR\s+([A-Z]+)\b", r"COLOR_\1", upper)

    tokens = re.findall(r"[A-Z_]+", upper)
    stop_words = {
        "JE",
        "BE",
        "JAVA",
        "BEDROCK",
        "EDITION",
        "BLOCK",
        "ITEM",
        "FOLIAGE",
        "TINT",
    }

    for index, token in enumerate(tokens):
        if token in stop_words:
            continue

        if token == "COLOR" and index + 1 < len(tokens):
            next_token = tokens[index + 1].lstrip("_")
            if next_token and next_token not in stop_words:
                return f"COLOR_{next_token}"

        if token.startswith("COLOR_"):
            return token

        if token.isalpha() and token not in stop_words:
            return token

    return None


def _extract_first_status_word(text: str) -> str | None:
    """Extract first status token among Yes/No/Partial."""
    match = re.search(r"\b(Yes|No|Partial)\b", text, flags=re.IGNORECASE)
    if not match:
        return None

    value = match.group(1).lower()
    return value.capitalize()


def _extract_first_number(text: str) -> str | None:
    """Extract first numeric token (int or float) from text."""
    match = re.search(r"\d+(?:\.\d+)?", text)
    return match.group(0) if match else None


def _extract_infobox_data(html: str, page_url: str) -> dict[str, Any]:
    """Parse selected infobox fields from a single block page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    infobox = soup.select_one("div.infobox")
    if infobox is None:
        raise ValueError(f"No infobox found for {page_url}")

    page_name = _page_title_from_url(page_url)
    title_tag = infobox.select_one(".infobox-title")
    title = _clean_text(title_tag.get_text(" ", strip=True)) if title_tag else page_name

    result: dict[str, Any] = {}

    image_tag = infobox.select_one(".infobox-imagearea img") or infobox.select_one("img")
    if image_tag is not None and image_tag.get("src"):
        result["Image"] = urljoin(BASE_URL, image_tag["src"])
    else:
        result["Image"] = None

    result["Name"] = title

    rows_table = infobox.select_one("table.infobox-rows")
    if rows_table is None:
        return result

    for row in rows_table.find_all("tr"):
        header = row.find("th", recursive=False)
        value_cell = row.find("td", recursive=False)
        if header is None or value_cell is None:
            continue

        key = _clean_text(header.get_text(" ", strip=True)).lower()
        value_text = _clean_text(value_cell.get_text(" ", strip=True))

        if key == "renewable":
            result["Renewable"] = value_text
        elif key == "stackable":
            result["Stackable"] = _extract_stackable_number(value_text)
        elif key == "tool":
            result["tool"] = _extract_tool_name(value_cell)
        elif key == "blast resistance":
            result["Blast resistance"] = value_text
        elif key == "hardness":
            result["Hardness"] = _extract_first_number(value_text)
        elif key == "luminous":
            result["Luminous"] = value_text
        elif key == "transparent":
            result["Transparent"] = _extract_first_status_word(value_text)
        elif key == "flammable":
            result["Flammable"] = _extract_first_status_word(value_text)
        elif key == "map color":
            result["Map_color"] = _extract_map_color(value_text)

    return result


def _save_blocks_file(blocks: dict[str, dict[str, Any]], output_path: Path) -> None:
    """Write current extraction state to disk."""
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(blocks, f, indent=1)



def download_blocks() -> None:
    """Build blocks.json by extracting infobox data for each Java Edition block."""
    # Extract a list of blocks
    page_title = "List_of_blocks_by_version"
    html = ""

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
    html = payload.get("parse", {}).get("text", "")

    if not html:
        print("API request succeeded but no HTML was returned.")
        return

    print("Website loaded successfully via MediaWiki API.")


    # Load versions.json as a dictionary
    output_dir = Path(__file__).resolve().parent
    versions_path = output_dir / "versions.json"
    versions : dict[str, str] = {}
    with versions_path.open("r", encoding="utf-8") as f:
        versions_dict = json.load(f)
        versions = {version: versions_dict[version] for version in versions_dict.keys()}




    # Extract data
    parser = Download_versions.JavaEditionVersionParser()
    parser.feed(html)

    data = parser.records
    print(f"Extracted {len(data)} block records from the Java Edition table.")


    # Process single block
    blocks: dict[str, dict[str, Any]] = {}
    output_dir = Path(__file__).resolve().parent
    blocks_path = output_dir / "blocks.json"
    processed_count = 0

    for record in data:
        try:
            url = record.get("LinkToWebsiteURL")
            if not url:
                continue

            if record.get("removed_version") is not None:
                processed_count += 1
                percentage : float = round((processed_count / len(data)) * 100, 2)
                print(f"({percentage}%) Skipping removed block: {record.get('Name', 'Unknown')}")
                continue
            

            resolved_url = url
            block_html = ""

            for _ in range(5):
                # Some entries resolve to redirect pages (e.g. /w/Planks#Oak).
                block_html = _page_html_from_url(resolved_url)
                redirect_url = _extract_redirect_url(block_html, resolved_url)

                if not redirect_url or redirect_url == resolved_url:
                    break

                resolved_url = redirect_url

            block_data = _extract_infobox_data(block_html, resolved_url)
            blocks[block_data["Name"]] = block_data
            blocks[block_data["Name"]]["Version"] = versions.get(record.get("version", ""), "") # type: ignore
            processed_count += 1
            percentage : float = round((processed_count / len(data)) * 100, 2)
            print(f"({percentage}%) Processed block: {block_data['Name']}")

            if processed_count % SAVE_EVERY == 0:
                _save_blocks_file(blocks, blocks_path)
                # print(f"Checkpoint saved after {processed_count} items.")


        except Exception as e:
            print("\n---- ERROR ----")
            print(f"Error processing record {record.get('Name', 'Unknown')}: {e}")
            print("")
            

    _save_blocks_file(blocks, blocks_path)
    print(f"Saved blocks to: {blocks_path}")



# Don't run the function again, the block-dataset is generated already

# if __name__ == "__main__":
#     download_blocks()






# def Test_block_load() -> None:
    
#     page_title = "Oak_Planks"
#     html = ""

#     # Call API
#     api_url = "https://minecraft.wiki/api.php"
#     params = {
#         "action": "parse",
#         "page": page_title,
#         "prop": "text",
#         "format": "json",
#         "formatversion": "2",
#     }
#     api_response = requests.get(api_url, params=params, timeout=20)
#     api_response.raise_for_status()
#     payload = api_response.json()
#     html = payload.get("parse", {}).get("text", "")

#     if not html:
#         print("API request succeeded but no HTML was returned.")
#         return

#     print("Website loaded successfully via MediaWiki API.")
    
#     with open("test_block.html", "w", encoding="utf-8") as f:
#         f.write(html)



# Test_block_load()