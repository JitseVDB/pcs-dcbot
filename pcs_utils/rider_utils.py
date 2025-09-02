from helpers.format_helper import reformat_name
from procyclingstats import Rider

def get_rider_team_history(name: str):
    pcs_name = reformat_name(name)
    try:
        rider = Rider(f"rider/{pcs_name}")
        return rider.teams_history()
    except Exception:
        return None