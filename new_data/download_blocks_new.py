import json
from helper import *


with open("versions.json") as f:
    ALL_VERSIONS = json.load(f)


table_html = get_from_api("List_of_blocks_by_version")
table_data = list_of_dict_from_table(table_html)

for dictionary in table_data:
    block_name = dictionary["block"]
    block_id = dictionary["id"]
    added_date = dictionary["added"]
    removed_date = dictionary["removed"]

    added_version = ALL_VERSIONS[added_date]
    removed_version = ALL_VERSIONS[removed_date]

    # TODO: Open html
    # TODO: Get html data
    # TODO: Save this under the name

