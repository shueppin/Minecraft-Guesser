import json
import re
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

import requests  # type: ignore


BASE_URL = "https://minecraft.wiki"


def _split_versions(cell_text: str) -> list[str]:
    text = unescape(cell_text).strip()
    if not text or text in {"-", "—"}:
        return []

    parts = re.split(r"\s*,\s*|\s+and\s+", text)
    return [part.strip() for part in parts if part.strip() and part.strip() not in {"-", "—"}]


def _first_version(cell_text: str) -> str | None:
    versions = _split_versions(cell_text)
    return versions[0] if versions else None


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", unescape(text)).strip()


class JavaEditionVersionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_java_section = False
        self.in_bedrock_section = False
        self.current_heading_id: str | None = None
        self.collect_heading_text = False
        self.heading_text_parts: list[str] = []

        self.current_row: list[str] | None = None
        self.current_row_link: str | None = None
        self.current_cell_parts: list[str] | None = None
        self.current_cell_href: str | None = None
        self.row_has_data_cell = False
        self.ignore_depth = 0

        self.records: list[dict[str, str | None]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)

        if tag == "h2":
            self.current_heading_id = attr_map.get("id")
            self.collect_heading_text = True
            self.heading_text_parts = []
            return

        if self.collect_heading_text:
            return

        if tag == "tr" and self.in_java_section and not self.in_bedrock_section:
            self.current_row = []
            self.current_row_link = None
            self.row_has_data_cell = False
            return

        if self.current_row is None:
            return

        if tag == "th":
            self.current_cell_parts = []
            self.current_cell_href = None
            return

        if tag == "td":
            self.current_cell_parts = []
            self.current_cell_href = None
            self.row_has_data_cell = True
            return

        if self.current_cell_parts is not None and tag == "a":
            href = attr_map.get("href")
            if href and self.current_row_link is None:
                self.current_cell_href = href

        if self.current_cell_parts is not None and tag == "sup":
            self.ignore_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.collect_heading_text:
            heading_text = re.sub(r"\s+", " ", "".join(self.heading_text_parts)).strip()
            if self.current_heading_id == "Java_Edition":
                self.in_java_section = True
                self.in_bedrock_section = False
            elif self.current_heading_id == "Bedrock_Edition":
                self.in_bedrock_section = True

            self.collect_heading_text = False
            self.current_heading_id = None
            self.heading_text_parts = []
            return

        if self.collect_heading_text:
            return

        if tag == "sup" and self.ignore_depth > 0:
            self.ignore_depth -= 1
            return

        if self.current_row is None:
            return

        if tag in {"td", "th"} and self.current_cell_parts is not None:
            cell_text = _clean_text("".join(self.current_cell_parts))
            self.current_row.append(cell_text)
            if self.current_row_link is None and len(self.current_row) == 1 and self.current_cell_href:
                self.current_row_link = urljoin(BASE_URL, self.current_cell_href)
            self.current_cell_parts = None
            self.current_cell_href = None
            return

        if tag == "tr":
            if self.row_has_data_cell and len(self.current_row) >= 4:
                name = self.current_row[0]
                if name:
                    record = {
                        "Name": name,
                        "LinkToWebsiteURL": self.current_row_link,
                        "version": _first_version(self.current_row[2]),
                        "removed_version": _first_version(self.current_row[3]),
                    }
                    self.records.append(record)

            self.current_row = None
            self.current_row_link = None
            self.current_cell_parts = None
            self.current_cell_href = None
            self.row_has_data_cell = False

    def handle_data(self, data: str) -> None:
        if self.collect_heading_text:
            self.heading_text_parts.append(data)
            return

        if self.current_cell_parts is not None and self.ignore_depth == 0:
            self.current_cell_parts.append(data)


def download_versions() -> None:
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



    # Extract data
    parser = JavaEditionVersionParser()
    parser.feed(html)

    data = parser.records
    print(f"Extracted {len(data)} block records from the Java Edition table.")



    # Process versions
    versions : list[str] = []
    for record in data:
        version = record.get("version")
        if version and version not in versions and record.get("removed_version") is None:
            versions.append(version)

    version_formated : dict[str, str] = {}
    for version in versions:
        version_formated[version] = ""



    # Save versions to JSON file
    output_dir = Path(__file__).resolve().parent

    versions_path = output_dir / "versions.json"
    with versions_path.open("w", encoding="utf-8") as f:
        json.dump(version_formated, f, indent=1)
    print(f"Saved versions to: {versions_path}")


# Never run this function again !!!
# download_versions()
    

