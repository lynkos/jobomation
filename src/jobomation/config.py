from jobomation.models import Company
from pathlib import Path
from yaml import safe_load

COMPANIES_CONFIG_PATH = Path("config/companies.yml")
FILTERS_CONFIG_PATH = Path("config/filters.yml")

def load_companies() -> list[Company]:
    with COMPANIES_CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = safe_load(file)

    return [
        Company(
            name=item["name"],
            source_type=item["source_type"],
            board_id=item["board_id"],
        )
        for item in config["companies"]
    ]

def load_filters() -> dict:
    with FILTERS_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return safe_load(file) or {}