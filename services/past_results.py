from pcs_scraper.race_result_scraper import get_rider_result_in_race
from pcs_scraper.rider_info_scraper import get_active_seasons

def get_past_results(name: str, race: str):
    """
    Retrieve past race results (finish positions) for a rider across all seasons.
    """
    active_seasons = get_active_seasons(name)
    results = {}

    for season in active_seasons:
        results[season] = get_rider_result_in_race(name, race, season)

    return results