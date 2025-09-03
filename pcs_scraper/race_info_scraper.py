from helpers.country_helper import get_flag_emoji_from_html
from helpers.url_formatter import race_url
from bs4 import BeautifulSoup
import requests

def get_race_flag(race: str):
    url = race_url(race)
    result = requests.get(url)
    result.raise_for_status()
    doc = BeautifulSoup(result.text, "html.parser")

    container = doc.find("div", class_="page-title")
    emoji = get_flag_emoji_from_html(container)

    return emoji



