from jobomation.models import CompanyConfig
from pathlib import Path
from yaml import safe_load

CONFIG_PATH = Path("config/companies.yml")

def load_companies() -> list[CompanyConfig]:
    with CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = safe_load(file)

    return [
        CompanyConfig(
            name=item["name"],
            source_type=item["source_type"],
            board_id=item["board_id"],
        )
        for item in config["companies"]
    ]