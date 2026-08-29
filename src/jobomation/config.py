from pathlib import Path
from yaml import safe_load
from jobomation.models import Target

TARGETS_CONFIG_PATH = Path("config/targets.yml")
"""Path to YAML config file with targets."""

FILTERS_CONFIG_PATH = Path("config/filters.yml")
"""Path to YAML config file with filters."""

def load_targets() -> list[Target]:
    """
    Load target definitions from YAML config file.

    Returns:
        list[Target]: List of Target objects built from each entry in config file.
    """
    with TARGETS_CONFIG_PATH.open("r", encoding = "utf-8") as file:
        config = safe_load(file)

    return [
        Target(
            name = item["name"],
            source = item["source"],
            args = item.get("args", { })
        )
        for item in config["targets"]
    ]

def load_filters() -> dict:
    """
    Load filtering rules from YAML config file.

    Returns:
        dict: Parsed filters, else empty dict if file empty.
    """
    with FILTERS_CONFIG_PATH.open("r", encoding = "utf-8") as file:
        return safe_load(file) or { }