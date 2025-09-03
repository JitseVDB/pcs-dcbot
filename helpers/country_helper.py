from bs4 import BeautifulSoup
import pycountry

def country_code_to_emoji(code: str) -> str:
    """
       Convert a 2-letter ISO country code to the corresponding flag emoji.

       Args:
           code (str): Two-letter ISO 3166-1 alpha-2 country code (e.g., "NL").

       Returns:
           str: Flag emoji if valid, otherwise the original input.
       """
    if len(code) != 2:
        return code  # fallback, return original if not 2 letters
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

def country_to_emoji(country_name):
    """
    Convert a country name to the corresponding flag emoji.

    Args:
        country_name (str): Full country name (e.g., "Netherlands").

    Returns:
        str: Flag emoji if the country is recognized, otherwise an empty string.
    """
    country = pycountry.countries.get(name=country_name)
    if not country:
        return ""

    # Convert ISO alpha-2 code to regional indicator symbols
    code = country.alpha_2.upper()
    return ''.join(chr(ord(c) + 127397) for c in code)

def get_flag_emoji_from_html(element) -> str:
    """
    Extract the first country flag from an HTML element or string and return it as an emoji.

    Args:
        element (str | bs4.element.Tag): Either a string containing HTML or a BeautifulSoup Tag
            that contains a <span> with a "flag" class representing a country code.

    Returns:
        str: The corresponding flag emoji if a valid 2-letter country code is found;
             otherwise, an empty string.
    """
    # If a string is passed, parse it
    if isinstance(element, str):
        soup = BeautifulSoup(element, "html.parser")
        flag_span = soup.find("span", class_="flag")
    else:
        # Already a Tag
        flag_span = element.find("span", class_="flag")

    if not flag_span:
        return ""

    classes = flag_span.get("class", [])
    country_code = next((cls.upper() for cls in classes if len(cls) == 2 and cls.isalpha()), None)

    if not country_code:
        return ""

    return chr(ord(country_code[0]) + 127397) + chr(ord(country_code[1]) + 127397)