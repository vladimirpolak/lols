from .client import HttpClient
from .models import Item
from .types import ContentType

from pathlib import Path
from urllib3.exceptions import ProtocolError

import logging
import requests
import retry


def progress_bar(total_size: int, downloaded_size):
    progress_bar_length = 50
    percent = int(downloaded_size * 100 / total_size)
    filled_length = int(progress_bar_length * downloaded_size / total_size)

    downloaded_mb = downloaded_size / 1000000
    total_mb = total_size / 1000000
    # Print the progress bar
    progress_bar = "[" + "=" * filled_length + " " * (progress_bar_length - filled_length) + "]"
    print(f"\r{percent}% {progress_bar} {downloaded_mb:.2f}/{total_mb:.2f} MB", end="")


class Downloader(HttpClient):
    def __init__(self,
                 session: requests.Session,
                 ):
        super().__init__(session)

    def download_item(self,
                      item: Item,
                      download_path: Path,
                      verbose: bool
                      ):
        response = self.send_request(
            method='GET',
            url=item.source,
            stream=True,
            headers=item.headers,
            **item.req_kwargs
        )
        response.raw.decode_content = True

        if not response.ok:
            logging.error(f"Failed request to '{item.source}', status code: '{response.status_code}'")
            logging.debug(f"Response headers: {response.headers}")
            return

        # Download the file and show the progress bar
        with download_path.open('wb') as f:
            total_size = int(response.headers.get("content-length", 0))
            if not total_size:
                logging.info(f"Downloading: {item.source}")
            downloaded_size = 0

            for data in response.iter_content(chunk_size=1024):

                # Write data to file

                f.write(data)
                # Update the downloaded size
                downloaded_size += len(data)

                # TODO Show progress bar under contition the instance is a command line app
                if total_size and verbose:
                    progress_bar(total_size, downloaded_size)
