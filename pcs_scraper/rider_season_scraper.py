from helpers.format_helper import reformat_name
from helpers.country_helper import country_code_to_emoji
from constants import rider_base_url
from bs4 import BeautifulSoup
import requests
import re

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

def get_season_results(name: str, season: int):
    """
    Scrape a rider's race results for a specific season from PCS.

    Parameters:
    name : str
        Rider's full name
    season : int
        Year of the season to scrape

    Returns:
    dict
        Race results as parsed by `parse_races`.
    """
    pcs_name = reformat_name(name)
    url = f"{rider_base_url}{pcs_name}/{season}"

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("div", id="rdrResultCont")
    if not container:
        return {}

    return parse_races(container)

def get_rider_program(name: str):
    """
    Scrape a rider's upcoming or planned races from their PCS profile.

    Args:
        name (str): Rider's full name (e.g., "Tadej Pogacar").

    Returns:
        list[dict[str, str]]: List of races, each represented as a dictionary with keys:
            - "date" (str): Date of the race (format as on PCS, e.g., "12.09").
            - "title" (str): Official race title.
            - "url" (str): Relative URL to the race's PCS page.
            - "flag" (str): Flag representing the race location.
    """
    pcs_name = reformat_name(name)
    url = rider_base_url + pcs_name

    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("ul", class_="list dashed flex pad2")
    if not container:
        return []

    races = []
    for li in container.find_all("li"):
        # Date
        date_div = li.find("div", class_="bold")
        date = date_div.get_text(strip=True) if date_div else ""

        # Title and race URL
        title_div = li.find("div", class_="ellipsis")
        race_a = title_div.find("a") if title_div else None
        title = race_a.get_text(strip=True) if race_a else ""
        race_url = race_a["href"] if race_a else ""

        # Flag
        flag_span = title_div.find("span", class_="flag") if title_div else None
        flag = flag_span["class"][-1] if flag_span and len(flag_span["class"]) > 1 else ""

        races.append({
            "date": date,
            "title": title,
            "url": race_url,
            "flag": country_code_to_emoji(flag)
        })

    return races