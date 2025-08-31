from constants import rider_base_url
from unidecode import unidecode
from bs4 import BeautifulSoup
import requests
import re

def reformat_name(name: str) -> str:
    """
    Reformat a rider's name into the ProCyclingStats (PCS) URL format.

    PCS rider URLs are structured as:
        https://www.procyclingstats.com/rider/{pcs_name}

    The PCS name is a normalized, lowercase, dash-separated string with no accents
    or special characters.

    Transformation steps:
        1. Convert accented characters to ASCII (e.g., "Pogačar" → "Pogacar").
        2. Convert to lowercase.
        3. Replace spaces with dashes.
        4. Remove all non-alphanumeric characters except dashes.
        5. Collapse multiple dashes into one.
        6. Strip leading/trailing dashes.

    Parameters:
    name : str
        The rider's full name (e.g., "Tadej Pogačar").

    Returns:
    str
        The normalized PCS-compatible rider name (e.g., "tadej-pogacar").
    """
    # Convert accented letters to ASCII equivalents
    name = unidecode(name)

    # Lowercase
    name = name.lower()

    # Replace spaces with dashes
    name = re.sub(r'\s+', '-', name)

    # Remove anything not a-z, 0-9, or dash
    name = re.sub(r'[^a-z0-9-]', '', name)

    # Remove consecutive dashes
    name = re.sub(r'-+', '-', name)

    # Strip leading/trailing dashes
    name = name.strip('-')

    return name

def country_code_to_emoji(code: str) -> str:
    """
    Convert a 2-letter ISO country code to the corresponding flag emoji.
    Example: 'nl' -> 🇳🇱
    """
    if len(code) != 2:
        return code  # fallback, return original if not 2 letters
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

def parse_races(container):
    """
    Parse race results from the ProCyclingStats results table.

    This function takes the `<div id="rdrResultCont">` container from a rider's
    PCS page and extracts structured information about the rider's races in
    the current season. It supports both one-day races and stage races, and
    correctly separates stage results from classification results.

    One-day races:
        Represented as a dictionary keyed by the race name (including category).
        Each entry contains:
            - date (str): race date (e.g. "04.03")
            - result (str): finishing position or "DNF"/"DNS"
            - flag (str): ISO country code from the flag icon (e.g. "nl", "be")
            - distance (str): race distance in km
            - pcs_points (str): PCS points earned (may be empty)
            - uci_points (str): UCI points earned (may be empty)

    Stage races:
        Represented as a dictionary keyed by the race name (including category).
        Each entry contains:
            - date_range (str): the overall date range of the stage race
                                (e.g. "22.03 › 26.03")
            - flag (str): ISO country code of the event
            - stages (list[dict]): list of stage dictionaries, each containing:
                - date (str): stage date
                - result (str): finishing position or "DNF"/"DNS"
                - distance (str): stage distance in km
                - pcs_points (str): PCS points earned (may be empty)
                - uci_points (str): UCI points earned (may be empty)
                - description (str): stage description or name
            - classifications (list[dict]): list of classification results, each containing:
                - name (str): classification name (e.g., "Youth classification")
                - result (str): finishing position in that classification
                - pcs_points (str): PCS points earned in the classification
                - uci_points (str): UCI points earned in the classification

    Parameters:
    container : bs4.element.Tag
        The BeautifulSoup object for the `<div id="rdrResultCont">` element.

    Returns:
    dict
        Dictionary of race results keyed by race name. Stage races include
        both `stages` and `classifications`.
    """
    tbody = container.find("tbody")
    if not tbody:
        return {}

    races = {}
    current_race = None

    for row in tbody.find_all("tr", recursive=False):
        classes = row.get("class", [])

        if "main" in classes:
            cols = row.find_all("td")
            if not cols:
                continue

            race_link = cols[4].find("a")
            race_name = race_link.get_text(strip=True) if race_link else "Unknown Race"
            race_name = re.sub(r'([^\s])(\(\d.*\))$', r'\1 \2', race_name)

            date_text = cols[0].get_text(" ", strip=True)

            flag = ""
            flag_span = cols[4].find("span", class_="flag")
            if flag_span and flag_span.get("class"):
                flag_classes = flag_span.get("class")
                country_code = flag_classes[1] if len(flag_classes) > 1 else ""
                flag = country_code_to_emoji(country_code)

            if "›" in date_text:  # stage race
                current_race = {"date_range": date_text, "flag": flag, "stages": [], "classifications": []}
                races[race_name] = current_race
            else:  # one-day race
                result = cols[1].get_text(strip=True)
                distance = cols[5].get_text(strip=True)
                pcs_points = cols[6].get_text(strip=True) if len(cols) > 6 else "0"
                uci_points = cols[7].get_text(strip=True) if len(cols) > 7 else "0"
                pcs_points = pcs_points if pcs_points else "0"
                uci_points = uci_points if uci_points else "0"

                races[race_name] = {
                    "date": date_text,
                    "result": result,
                    "flag": flag,
                    "distance": distance,
                    "pcs_points": pcs_points,
                    "uci_points": uci_points
                }
                current_race = None

        elif "stage" in classes and current_race:
            cols = row.find_all("td")
            if not cols:
                continue

            stage_name_link = cols[4].find("a")
            stage_name = stage_name_link.get_text(" ", strip=True) if stage_name_link else ""

            # Detect classification rows by presence of "classification" in name
            if "classification" in stage_name.lower():
                class_name = stage_name
                result = cols[1].get_text(strip=True) or "-"
                pcs_points = cols[6].get_text(strip=True) if len(cols) > 6 else "0"
                uci_points = cols[7].get_text(strip=True) if len(cols) > 7 else "0"
                pcs_points = pcs_points if pcs_points else "0"
                uci_points = uci_points if uci_points else "0"

                current_race["classifications"].append({
                    "name": class_name,
                    "result": result,
                    "pcs_points": pcs_points,
                    "uci_points": uci_points
                })
                continue  # skip adding to stages

            # Otherwise, normal stage row
            date_text = cols[0].get_text(strip=True)
            result = cols[1].get_text(strip=True)
            distance = cols[5].get_text(strip=True)
            pcs_points = cols[6].get_text(strip=True) if len(cols) > 6 else "0"
            uci_points = cols[7].get_text(strip=True) if len(cols) > 7 else "0"
            pcs_points = pcs_points if pcs_points else "0"
            uci_points = uci_points if uci_points else "0"

            stage_desc = re.sub(r'^S\d+\s+', '', stage_name)

            stage_info = {
                "date": date_text,
                "result": result,
                "distance": distance,
                "pcs_points": pcs_points,
                "uci_points": uci_points,
                "description": stage_desc
            }

            current_race["stages"].append(stage_info)

    return races

def get_season_results(name: str):
    """
    Scrape ProCyclingStats (PCS) for a rider's season results.

    This function takes a rider's full name, reformats it into the PCS URL format,
    fetches the rider's results page, and parses the results table into a structured
    dictionary. Both one-day races and stage races are supported.

    For one-day races:
        The dictionary entry is keyed by the race name (including its UCI category),
        and the value contains race details such as date, result, flag, distance,
        PCS points, and UCI points.

    For stage races:
        The dictionary entry is keyed by the stage race name (including its UCI category),
        and the value contains the overall date range, flag, and a list of stage results.
        Each stage result is represented as a dictionary with the same fields as
        one-day races (except the flag is usually omitted at the stage level).

    Parameters:
    name : str
        Rider's full name (e.g. "Bas Tietema", "Jasper Philipsen").

    Returns:
    dict
        Dictionary of race results for the season, keyed by race name.
    """
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")
    container = doc.find("div", id="rdrResultCont")

    if not container:
        print(f"No results found for {name} at {url}")
        return {}

    return parse_races(container)