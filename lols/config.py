from datetime import datetime
from pathlib import Path
import logging
import json


def base_dir(dir_name: str = "config"):
    path = Path().cwd() / dir_name
    if not path.exists():
        path.mkdir()
    return path


class Manager:
    """
    Class responsible for managing saving and loading of auth data for scrapers that require credentials.
    """
    @staticmethod
    def load_config(domain_name) -> dict:
        path = base_dir() / f"{domain_name}.json"

        if not path.exists():
            return {}

        with path.open("r") as file:
            data = json.load(file)

        iso_date = data["created_at"]
        data["created_at"] = datetime.fromisoformat(iso_date)
        return data

    @staticmethod
    def save_config(domain_name, data: dict):
        path = base_dir() / f"{domain_name}.json"

        data["created_at"] = datetime.now().isoformat()

        logging.info(
            f"Creating new auth config for {domain_name}\n"
            f"Data: {data}"
        )
        with path.open("w") as file:
            json.dump(data, file, indent=6)
