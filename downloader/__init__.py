import time
import requests
from pathlib import Path
import retry
from .headers import HeadersMixin
from tqdm.auto import tqdm
from urllib3.exceptions import ProtocolError
from .models import Item
import shutil
import logging


class Downloader(HeadersMixin):
    OUTPUT_DIR = "Output"
    IMAGES_DIR_NAME = "Images"
    VIDEOS_DIR_NAME = "Videos"
    ARCHIVES_DIR_NAME = "Archives"
    AUDIO_DIR_NAME = "Audio"

    def __init__(self,
                 session: requests.Session
                 ):
        self._session = session

    def set_session(self, session: requests.Session):
        self._session = session

    def send_request(self, url, method, **kwargs) -> requests.Response:
        prepped_req = self._prepare_request(
            url=url,
            method=method,
            **kwargs
        )
        response = self._send_request(prepped_req, **kwargs)
        return response

    def _prepare_request(self, method: str, url: str, **kwargs) -> requests.PreparedRequest:
        headers = self.general_headers
        headers.update(kwargs.pop("headers", dict()))

        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            data=kwargs.pop("data", None),
            params=kwargs.pop("params", None),
            cookies=kwargs.pop("cookies", None)
        )
        return self._session.prepare_request(req)

    @retry.retry(requests.exceptions.RequestException, tries=3, delay=3)
    def _send_request(self, prepared_request, **kwargs) -> requests.Response:
        res = self._session.send(
            request=prepared_request,
            stream=kwargs.pop("stream", None)
        )
        if res.status_code == 429:
            time.sleep(10)
            raise requests.exceptions.RequestException
                      # stream=stream,
                      # verify=verify,
                      # proxies=proxies,
                      # cert=cert,
                      # timeout=timeout
        return res

    @retry.retry(
        (requests.exceptions.RequestException, ProtocolError),
        tries=3,
        delay=5
    )
    def download_item(self,
                      item: Item,
                      separate_content: bool,
                      save_urls: bool,
                      album_name: str = None
                      ):
        album_dir = album_name or item.album_title or input(
            f"Enter the name for album directory: "
        )
        album_path = self.output_path / album_dir

        # Set download path
        if separate_content:
            if item.content_type == "image":
                dl_dir_path = album_path / self.IMAGES_DIR_NAME
            elif item.content_type == "video":
                dl_dir_path = album_path / self.VIDEOS_DIR_NAME
            elif item.content_type == "archive":
                dl_dir_path = album_path / self.ARCHIVES_DIR_NAME
            elif item.content_type == "audio":
                dl_dir_path = album_path / self.AUDIO_DIR_NAME
        else:
            dl_dir_path = album_path

        if not dl_dir_path.exists():
            dl_dir_path.mkdir(parents=True)

        file_path = dl_dir_path / (item.filename + item.extension)

        if file_path.exists():
            logging.debug(f"Filename already exists: {item}")
            return

        print(f"Downloading: {item.source}\n")
        # Make request
        response = self.send_request(
            method='GET',
            url=item.source,
            stream=True
        )
        response.raw.decode_content = True

        if self.is_invalid(response):
            return

        try:
            total_size = int(response.headers.get('Content-Length'))
        except TypeError:
            logging.error(
                f"Error when extracting 'content-length from {item.source} response."
            )

            # Download without progress bar
            with open(file_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)
        else:
            with tqdm.wrapattr(response.raw, "read", total=total_size, desc="") as raw:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(raw, f)

            if save_urls:
                with open(album_path / "urls.txt", "a") as f:
                    f.write(item.source)
                    f.write("\n")

    @classmethod
    def is_invalid(cls, response: requests.Response) -> bool:
        if response.status_code >= 400:
            return True

    @property
    def output_path(self):
        return self._create_path(self.OUTPUT_DIR)

    def _create_path(self, dirname_or_absolutepath: str):
        path = Path(dirname_or_absolutepath)
        if path.is_absolute():
            return path
        else:
            return Path().cwd() / dirname_or_absolutepath

    def update_cookies(self, cookies: dict, domain: str):
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain=domain)