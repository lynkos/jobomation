from html import unescape
from bs4 import BeautifulSoup

def clean_description(content: str) -> str:
    decoded = unescape(content)
    soup = BeautifulSoup(decoded, "html.parser")
    return soup.get_text(separator="\n", strip=True)