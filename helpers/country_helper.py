import pycountry

def country_code_to_emoji(code: str) -> str:
    """
    Convert a 2-letter ISO country code to the corresponding flag emoji.
    Example: 'nl' -> 🇳🇱
    """
    if len(code) != 2:
        return code  # fallback, return original if not 2 letters
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)

def country_to_emoji(country_name):
    country = pycountry.countries.get(name=country_name)
    if not country:
        return ""

    # Convert ISO alpha-2 code to regional indicator symbols
    code = country.alpha_2.upper()
    return ''.join(chr(ord(c) + 127397) for c in code)