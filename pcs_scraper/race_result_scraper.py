from helpers.url_formatter import race_result_url
from bs4 import BeautifulSoup
import requests

def get_rider_result_in_race(name: str, race: str, season: int) -> str | None:
    """
    Retrieve the finish position of a given rider in a specific race & season.

    Args:
        name (str): Rider's full name in natural order (e.g. "Mathieu van der Poel").
        race (str): Race name (will be formatted for PCS).
        season (int): The year of the race.

    Returns:
        str | None: The rider's finish position (rank) as text, or None if not found.
    """
    normalized_input = name.lower().replace(" ", "-")

    url = race_result_url(race, season)
    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("div", class_="borderbox w68 left mb_w100")
    if not container:
        return None

    table = container.find("table", class_="results")
    if not table:
        return None

    for row in table.find("tbody").find_all("tr"):
        rider_cell = row.find("td", class_="ridername")
        if not rider_cell:
            continue

        rider_link = rider_cell.find("a")
        if not rider_link:
            continue

        href = rider_link.get("href", "").lower()  # e.g. "rider/mathieu-van-der-poel"
        if normalized_input in href:
            return row.find("td").get_text(strip=True)  # rank column

    return None