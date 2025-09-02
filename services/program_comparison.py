from pcs_scraper.rider_season_scraper import get_rider_program
from typing import List, Dict

def compare_programs(name1: str, name2: str) -> List[Dict]:
    """
    Compare the upcoming programs of two riders.

    Args:
        name1 (str): Full name of the first rider.
        name2 (str): Full name of the second rider.

    Returns:
        list[dict]: List of races with participation info. Each dict contains:
            - "date" (str): Race date (from PCS, e.g., "12.09").
            - "title" (str): Race title.
            - "flag" (str): Race flag emoji.
            - "name1_participating" (bool): True if name1 is racing.
            - "name2_participating" (bool): True if name2 is racing.
    """
    # Get race programs for both riders
    program1 = get_rider_program(name1)
    program2 = get_rider_program(name2)

    # Map races by title + date to combine them
    combined = {}

    for race in program1:
        key = (race["title"], race["date"])
        combined[key] = {
            "date": race["date"],
            "title": race["title"],
            "flag": race["flag"],
            "name1_participating": True,
            "name2_participating": False
        }

    for race in program2:
        key = (race["title"], race["date"])
        if key in combined:
            combined[key]["name2_participating"] = True
        else:
            combined[key] = {
                "date": race["date"],
                "title": race["title"],
                "flag": race["flag"],
                "name1_participating": False,
                "name2_participating": True
            }

    # Return as a list sorted by date (optional: sort by month/day)
    def sort_key(r):
        day, month = r["date"].split(".")
        return int(month), int(day)

    return sorted(combined.values(), key=sort_key)