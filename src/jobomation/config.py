from pathlib import Path
from yaml import safe_load
from jobomation.models import Target

TARGETS_CONFIG_PATH = Path("config/targets.yml")
FILTERS_CONFIG_PATH = Path("config/filters.yml")

def load_targets() -> list[Target]:
    with TARGETS_CONFIG_PATH.open("r", encoding="utf-8") as file:
        config = safe_load(file)

    return [
        Target(
            name=item["name"],
            source_type=item["source_type"],
            args=item.get("args", {}),
        )
        for item in config["targets"]
    ]

def load_filters() -> dict:
    with FILTERS_CONFIG_PATH.open("r", encoding="utf-8") as file:
        return safe_load(file) or {}