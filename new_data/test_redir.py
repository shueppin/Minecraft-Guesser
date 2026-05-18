import Download_blocks
url = "https://minecraft.wiki/w/Oak_Planks"
html = Download_blocks._page_html_from_url(url)
redir = Download_blocks._extract_redirect_url(html, url)
print(f"Original: {url}")
print(f"Redirect: {redir}")
target_html = Download_blocks._page_html_from_url(redir) if redir else html
data = Download_blocks._extract_infobox_data(target_html)
if data:
    print(f"Name_found: {data.get('Name')}")
    print(f"Image_present: {bool(data.get('Image'))}")
else:
    print("No infobox data found.")
