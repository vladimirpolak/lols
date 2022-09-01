from pathlib import Path
from datetime import datetime
import logging
import json


def base_dir(dir_name: str = "config"):
    path = Path().cwd() / dir_name
    if not path.exists():
        path.mkdir()
    return path


class Manager:
    @staticmethod
    def load_config(domain_name) -> dict:
        base_directory = base_dir()
        path = base_directory / f"{domain_name}.json"

        if not path.exists():
            return {}
        data = json.load(path.open("r"))
        iso_date = data["created_at"]
        data["created_at"] = datetime.fromisoformat(iso_date)

        return data

    @staticmethod
    def save_config(domain_name, data: dict):
        base_directory = base_dir()
        path = base_directory / f"{domain_name}.json"

        data["created_at"] = datetime.now().isoformat()

        logging.debug(
            f"Creating new auth config for {domain_name}\n"
            f"Data: {data}"
        )
        json.dump(data, path.open("w"), indent=6)
