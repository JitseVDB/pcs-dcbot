from helpers.format_helper import reformat_name
from constants import rider_base_url
from bs4 import BeautifulSoup
import requests
import re

def normalize_key(text: str) -> str:
    """
    Convert category names from the page into snake_case keys.
    Examples:
        "Onedayraces" -> "one_day_races"
        "GC"          -> "gc"
        "TT"          -> "time_trial"
    """
    text = text.strip().lower()
    replacements = {
        "onedayraces": "one_day_races",
        "gc": "gc",
        "tt": "time_trial",
        "sprint": "sprint",
        "climber": "climber",
        "hills": "hills",
    }
    return replacements.get(text, re.sub(r"\s+", "_", text))

def get_points_per_speciality(name: str) -> dict[str, int]:
    """
    Scrape a rider's PCS profile and extract points per speciality.

    Args:
        name (str): Rider's full name (e.g., "Tadej Pogacar").

    Returns:
        dict[str, int]: Dictionary mapping speciality -> points.
    """
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    # Fetch and parse rider page
    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("ul", class_="pps list")
    data = {}

    if container:
        for li in container.find_all("li"):
            value = int(li.select_one(".xvalue").text.strip())
            category = li.select_one(".xtitle a").text.strip()
            key = normalize_key(category)
            data[key] = value

    return data

def get_points_per_season(name: str) -> list[dict[str, int]]:
    """
      Scrape a rider's PCS profile and extract ranking points per season.

      Args:
          name (str): Rider's full name (e.g., "Tadej Pogacar").

      Returns:
          list[dict[str, int]]: A list of dictionaries, one per season, with keys:
              - "season" (int): Year of the season.
              - "points" (int): PCS points earned that season.
              - "rank" (int): Rider's PCS ranking position for that season.
    """
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    resp = requests.get(url)
    resp.raise_for_status()
    doc = BeautifulSoup(resp.text, "html.parser")

    # Find the section header (be flexible on exact casing/text)
    header = doc.find("h4", string=re.compile(r"PCS Ranking position per season", re.I))
    if not header:
        return []  # section not found

    pcs_block = header.find_parent("div", class_="mt20")
    if not pcs_block:
        return []  # layout changed

    ranking_list: list[dict[str, int]] = []
    for tr in pcs_block.select("table tbody tr"):
        tds = tr.find_all("td")
        if len(tds) < 3:
            continue

        # season is usually the first cell (with a link)
        season_text = tds[0].get_text(strip=True)
        season = int(re.sub(r"[^\d]", "", season_text) or 0)

        # points might be inside a nested element; fall back to the second cell's text
        pts_node = tr.select_one("td .title")
        pts_text = (pts_node.get_text(strip=True) if pts_node else tds[1].get_text(strip=True))
        points = int(re.sub(r"[^\d]", "", pts_text) or 0)

        # rank is typically the last cell
        rank_text = tds[-1].get_text(strip=True)
        rank = int(re.sub(r"[^\d]", "", rank_text) or 0)

        ranking_list.append({"season": season, "points": points, "rank": rank})

    return ranking_list