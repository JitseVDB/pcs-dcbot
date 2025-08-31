def country_code_to_emoji(code: str) -> str:
    """
    Convert a 2-letter ISO country code to the corresponding flag emoji.
    Example: 'nl' -> 🇳🇱
    """
    if len(code) != 2:
        return code  # fallback, return original if not 2 letters
    return chr(ord(code[0].upper()) + 127397) + chr(ord(code[1].upper()) + 127397)