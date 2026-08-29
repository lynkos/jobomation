from html import unescape
from bs4 import BeautifulSoup

def clean_description(content: str) -> str:
    """
    Convert raw HTML to readable plain-text.

    Args:
        content (str): Raw HTML string.

    Returns:
        str: Plain-text content with decoded HTML.
    """
    decoded = unescape(content)
    soup = BeautifulSoup(decoded, "html.parser")
    return soup.get_text(separator = "\n", strip = True)