from pathlib import Path
from datetime import datetime
import logging
import json


class Manager:
    @classmethod
    def load_config(cls, domain_name) -> dict:
        path = Path().cwd() / "config" / f"{domain_name}.json"

        if not path.exists():
            return {}
        data = json.load(path.open("r"))
        iso_date = data["created_at"]
        data["created_at"] = datetime.fromisoformat(iso_date)

        return data

    @classmethod
    def save_config(cls, domain_name, data: dict):
        path = Path().cwd() / "config" / f"{domain_name}.json"

        data["created_at"] = datetime.now().isoformat()

        logging.debug(
            f"Creating new auth config for {domain_name}\n"
            f"Data: {data}"
        )
        json.dump(data, path.open("w"), indent=6)
