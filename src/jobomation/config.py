from jobomation.models import Company
from pathlib import Path
from yaml import safe_load

CONFIG_PATH = Path("config/companies.yml")

def load_companies() -> list[Company]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = safe_load(file)

    return [
        Company(
            name=item["name"],
            source_type=item["source_type"],
            board_id=item["board_id"],
        )
        for item in config["companies"]
    ]