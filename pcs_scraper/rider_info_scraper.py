from helpers.format_helper import reformat_name
from constants import rider_base_url, pcs_base_url
from bs4 import BeautifulSoup
import requests

_rider_cache = {}  # in-memory cache

def _fetch_rider_info(name: str):
    """
    Fetch and parse rider information from ProCyclingStats (PCS).

    This function scrapes the rider's PCS page for personal details such as
    date of birth, age, weight, height, nationality, and place of birth.
    Results are cached in `_rider_cache` to avoid repeated network requests.

    Parameters:
    name : str
        Full name of the rider (e.g., "Tadej Pogačar").

    Returns:
    dict
        Dictionary containing rider information with keys:
            - "date_of_birth" : str, e.g., "21st September 1998"
            - "age"           : str, e.g., "26"
            - "weight"        : str, e.g., "66 kg"
            - "height"        : str, e.g., "1.76 m"
            - "nationality"   : str, e.g., "Slovenia"
            - "place_of_birth": str, e.g., "Klanec"

        Returns an empty dictionary if the rider's information cannot be found.
    """
    if name in _rider_cache:
        return _rider_cache[name]

    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")
    container = doc.find("div", class_="borderbox left w65")

    if not container:
        print(f"No results found for {name} at {url}")
        return {}

    rider_info = {}

    for ul in container.find_all("ul", class_="list"):
        for li in ul.find_all("li"):
            label_div = li.find("div", class_="bold mr5")
            if not label_div:
                continue

            label = label_div.text.strip().rstrip(":").lower()
            values = [div.text.strip() for div in li.find_all("div") if div != label_div]

            if label == "date of birth":
                rider_info["date_of_birth"] = " ".join(values[:3])
                for v in values[3:]:
                    if v.isdigit():
                        rider_info["age"] = v
                        break
            elif label == "weight":
                rider_info["weight"] = values[0] + " " + values[1]
                rider_info["height"] = values[3] + " " + values[4]
            elif label == "nationality":
                rider_info["nationality"] = values[-1]
            elif label == "place of birth":
                rider_info["place_of_birth"] = values[-1]

    _rider_cache[name] = rider_info
    return rider_info

# single-field getters
def get_rider_birthdate(name: str):
    """Return the rider's date of birth as a string (e.g., '21st September 1998')."""
    return _fetch_rider_info(name).get("date_of_birth")

def get_rider_age(name: str):
    """Return the rider's age as a string (e.g., '26')."""
    return _fetch_rider_info(name).get("age")

def get_rider_place_of_birth(name: str):
    """Return the rider's place of birth as a string (e.g., 'Klanec')."""
    return _fetch_rider_info(name).get("place_of_birth")

def get_rider_weight(name: str):
    """Return the rider's weight as a string (e.g., '66 kg')."""
    return _fetch_rider_info(name).get("weight")

def get_rider_height(name: str):
    """Return the rider's height as a string (e.g., '1.76 m')."""
    return _fetch_rider_info(name).get("height")

def get_rider_nationality(name: str):
    """Return the rider's nationality as a string (e.g., 'Slovenia')."""
    return _fetch_rider_info(name).get("nationality")

def get_rider_image_url(name: str):
    """
    Fetch the profile image URL for a rider from ProCyclingStats (PCS).

    Args:
        name (str): Rider's full name in plain text (e.g., "Tadej Pogacar").
                    This will be reformatted with `reformat_name()` to match PCS URL conventions.

    Returns:
        str: The full absolute URL to the rider's profile image.

    Raises:
        requests.HTTPError: If the request to the rider page fails (e.g., 404 or 500).
        AttributeError: If no <img> tag is found on the rider's profile page.
    """
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")
    img_src = doc.find("img")["src"]
    return pcs_base_url + img_src

def get_active_seasons(name: str):
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("ul", class_="rdrSeasonNav")
    if not container:
        return []

    # Extract all seasons from links
    seasons = []
    for a in container.find_all("a", class_="rdrFilterSeason"):
        season = a.get("data-season")
        if season:
            seasons.append(int(season))

    return seasons
