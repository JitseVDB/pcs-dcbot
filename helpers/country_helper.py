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