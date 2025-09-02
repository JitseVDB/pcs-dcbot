from constants import MAX_FIELD_LENGTH, MAX_EMBED_DESCRIPTION_LENGTH
from unidecode import unidecode
import discord
import re

def reformat_name(name: str) -> str:
    """
    Reformat a rider's name into the ProCyclingStats (PCS) URL format.

    PCS rider URLs are structured as:
        https://www.procyclingstats.com/rider/{pcs_name}

    The PCS name is a normalized, lowercase, dash-separated string with no accents
    or special characters.

    Transformation steps:
        1. Convert accented characters to ASCII (e.g., "Pogačar" → "Pogacar").
        2. Convert to lowercase.
        3. Replace spaces with dashes.
        4. Remove all non-alphanumeric characters except dashes.
        5. Collapse multiple dashes into one.
        6. Strip leading/trailing dashes.

    Parameters:
    name : str
        The rider's full name (e.g., "Tadej Pogačar").

    Returns:
    str
        The normalized PCS-compatible rider name (e.g., "tadej-pogacar").
    """
    # Convert accented letters to ASCII equivalents
    name = unidecode(name)

    # Lowercase
    name = name.lower()

    # Replace spaces with dashes
    name = re.sub(r'\s+', '-', name)

    # Remove anything not a-z, 0-9, or dash
    name = re.sub(r'[^a-z0-9-]', '', name)

    # Remove consecutive dashes
    name = re.sub(r'-+', '-', name)

    # Strip leading/trailing dashes
    name = name.strip('-')

    return name

def split_text_preserving_lines(text, max_len=MAX_FIELD_LENGTH):
    """
        Split text into chunks of at most `max_len` characters without breaking lines.

        Args:
            text (str): Input text to split.
            max_len (int): Maximum allowed length of each chunk. Defaults to MAX_FIELD_LENGTH.

        Returns:
            list[str]: List of text chunks, each no longer than `max_len`.
        """
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks


def split_embed_preserving_lines(text, max_len=MAX_EMBED_DESCRIPTION_LENGTH):
    """
    Split text into chunks of at most `max_len` characters without breaking lines.
    """
    lines = text.split("\n")
    chunks = []
    current = ""
    for line in lines:
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks