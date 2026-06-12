#utils.py
from config import *
import unicodedata
import re

def clean_header_title(title: str) -> str:
    """
    Normalizes a string by stripping markdown characters, emojis, 
    diacritics, punctuation, and all spaces to create an identical match key.
    """
    # Remove markdown header syntax and common emojis/punctuation characters
    title = re.sub(r'[#\d🏛️🎓▶️🔹♦️▪️\-–—_:.,()\[\]]', '', title)
    
    # Decompose character accents (e.g., 'ă' becomes 'a' + combining breve accent)
    title = unicodedata.normalize('NFKD', title)
    
    # Filter out the combining diacritic marks, leaving only basic ASCII characters
    title = "".join([c for c in title if not unicodedata.combining(c)])
    
    # Lowercase and remove all remaining spaces for absolute comparison stability
    return "".join(title.lower().split())


def clean_header(title: str) -> str:
    """Strips markdown syntax, punctuation, and spaces for fuzzy matching."""
    return re.sub(r'[#\d\s\-:.,]', '', title).lower().strip()


def log_error(message: str):
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(message.strip() + "\n")