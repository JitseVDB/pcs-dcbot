from helpers.format_helper import reformat_name
from constants import rider_base_url
from bs4 import BeautifulSoup
import requests
import re

def get_rider_team_history(name: str):
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    # Fetch and parse rider page
    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("ul", class_="rdr-teams2")
    if not container:
        return []

    history = []
    for li in container.find_all("li", class_="main"):  # only season-specific rows
        season_text = li.find("div", class_="season").get_text(strip=True)
        if not season_text.isdigit():
            continue
        season = int(season_text)

        name_div = li.find("div", class_="name")
        if not name_div:
            continue

        a = name_div.find("a")
        team_name = a.get_text(strip=True)
        team_url = a["href"]

        # team class is inside parentheses after the link text
        class_match = re.search(r"\(([^)]+)\)", name_div.get_text())
        team_class = class_match.group(1).strip() if class_match else ""

        history.append({
            "season": season,
            "team_name": team_name,
            "team_url": team_url,
            "class": team_class,
            "since": "01-01",
            "until": "12-31"
        })

    return history