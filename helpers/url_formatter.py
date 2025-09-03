from helpers.format_helper import reformat_name

def race_result_url(name: str, season: int) -> str:
    """
    Build the URL for a race result on ProCyclingStats.

    Args:
        name (str): The race name (will be reformatted to PCS URL format).
        season (int): The season year

    Returns:
        str: The formatted PCS race URL.
    """
    return f"https://www.procyclingstats.com/race/{reformat_name(name)}/{season}/result"

def race_url(name: str) -> str:
    """
        Build the URL for a race result on ProCyclingStats.

        Args:
            name (str): The race name (will be reformatted to PCS URL format).

        Returns:
            str: The formatted PCS race URL.
        """
    return f"https://www.procyclingstats.com/race/{reformat_name(name)}"