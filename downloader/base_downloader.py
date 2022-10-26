import time
import requests
from pathlib import Path
import retry
from .headers import HeadersMixin
from console import console
from urllib3.exceptions import ProtocolError
from .models import Item
from .types import ContentType
from rich.progress import wrap_file
from .m3u8 import M3u8Downloader
import shutil
import logging


class Downloader(HeadersMixin):
    OUTPUT_DIR = "Output"
    IMAGES_DIR_NAME = "Images"
    VIDEOS_DIR_NAME = "Videos"
    ARCHIVES_DIR_NAME = "Archives"
    AUDIO_DIR_NAME = "Audio"

    def __init__(self,
                 session: requests.Session,
                 download_path: str = None
                 ):
        self._session = session
        self.custom_download_path = download_path

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
            stream=True if kwargs.pop("stream", None) else None,
            allow_redirects=False if kwargs.pop("allow_redirects", None) is False else True
        )
        if res.status_code == 429:
            time.sleep(10)
            raise requests.exceptions.RequestException
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
                      album_name: str = None,
                      curr_item_num: int = None,
                      total_length: int = None,
                      skip_existing: bool = False,
                      overwrite_existing: bool = False
                      ):
        album_dir = album_name or item.album_title or input(
            f"Enter the name for album directory: "
        )
        album_path = self.output_path / album_dir

        # Set download path
        if separate_content:
            dl_dir_path = album_path / self.contenttype_dir(item.content_type)
        else:
            dl_dir_path = album_path

        # Create download directory
        if not dl_dir_path.exists():
            dl_dir_path.mkdir(parents=True)

        # Create file path
        file_path = self.generate_download_path(
            download_directory=dl_dir_path,
            download_item=item,
            skip_existing=skip_existing,
            overwrite_existing=overwrite_existing
        )
        if file_path is None:
            logging.debug(f"Filename already exists, skipping: {item}")
            return

        if item.content_type == ContentType.M3U8:
            self.m3u8_download(stream_url=item.source, file_path=file_path)
            return

        progress_info = ""
        if curr_item_num:
            progress_info = f"[bright_cyan]{curr_item_num}[/bright_cyan]/" \
                            f"[bright_cyan]{total_length}[/bright_cyan]"

        console.print(f"\nURL: {item.source}")
        # Make request
        response = self.send_request(
            method='GET',
            url=item.source,
            stream=True,
            headers=item.headers
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

            console.print(f"Downloading {progress_info} [dark_red]...progress not available...[/dark_red]")
            # Download without progress bar
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
        else:
            # RICH Progress bar
            with wrap_file(response.raw,
                           total=total_size,
                           refresh_per_second=30,
                           description=f"Downloading {progress_info}",
                           console=console) as raw:
                with open(file_path, 'wb') as f:
                    shutil.copyfileobj(raw, f)

        if save_urls:
            with open(album_path / "urls.txt", "a") as f:
                f.write(item.source)
                f.write("\n")

    def m3u8_download(self, stream_url, file_path):
        downloader = M3u8Downloader(
            url=stream_url,
            output_filename=file_path,
            session=self._session
        )

        downloader.start()

    @staticmethod
    def generate_download_path(
            download_directory: Path,
            download_item: Item,
            skip_existing: bool,
            overwrite_existing: bool,
            step: int = 1):
        file_path = download_directory / (download_item.filename + download_item.extension)

        if file_path.exists():
            if skip_existing is False:
                if overwrite_existing:
                    file_path = download_directory / (download_item.filename + download_item.extension)
                    return file_path
                else:
                    while True:
                        file_path = download_directory / (
                                    f'{download_item.filename} ({step})' + download_item.extension)
                        if not file_path.exists():
                            break
                        step += 1
                    return file_path
            else:
                return None
        return file_path

    @classmethod
    def is_invalid(cls, response: requests.Response) -> bool:
        if response.status_code >= 400:
            return True

    @classmethod
    def contenttype_dir(cls, content_type: ContentType) -> str:
        if content_type == ContentType.IMAGE:
            return cls.IMAGES_DIR_NAME
        elif content_type == ContentType.VIDEO or \
                content_type == ContentType.M3U8:
            return cls.VIDEOS_DIR_NAME
        elif content_type == ContentType.ARCHIVE:
            return cls.ARCHIVES_DIR_NAME
        elif content_type == ContentType.AUDIO:
            return cls.AUDIO_DIR_NAME

    @property
    def output_path(self):
        if self.custom_download_path:
            return self._create_path(self.custom_download_path)
        return self._create_path(self.OUTPUT_DIR)

    @staticmethod
    def _create_path(dirname_or_absolutepath: str):
        path = Path(dirname_or_absolutepath)
        if path.is_absolute():
            return path
        else:
            return Path().cwd() / dirname_or_absolutepath

    def update_cookies(self, cookies: dict, domain: str):
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain=domain)
