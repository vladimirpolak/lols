import requests
from pathlib import Path
import retry
from .headers import HeadersMixin
from collections import ChainMap
import shutil
import logging


class Item:
    content_type: str  # image/video/archive
    album_title: str
    filename: str
    extension: str  # .jpg/.mp4...
    source: str

    def __init__(self, content_type: str, filename: str, extension: str, source: str, album_title: str = None):
        self.content_type = content_type
        self.album_title = album_title
        self.filename = filename
        self.extension = extension
        self.source = source

    def __str__(self):
        return f"Item(" \
               f"{self.filename}{self.extension}, " \
               f"{self.source}" \
               f")"

    def __repr__(self):
        return f"Item(" \
               f"content_type={self.content_type}, " \
               f"album_title={self.album_title}, " \
               f"filename={self.filename}, " \
               f"extension={self.extension}, " \
               f"source={self.source}" \
               f")"


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

    @property
    def output_path(self):
        return self._create_path(self.OUTPUT_DIR)

    def _create_path(self, dirname_or_absolutepath: str):
        path = Path(dirname_or_absolutepath)
        if path.is_absolute():
            return path
        else:
            return Path().cwd() / dirname_or_absolutepath

    def set_session(self, session: requests.Session):
        self._session = session

    @retry.retry(requests.exceptions.RequestException, tries=3, delay=3)
    def get_page(self,
                 url_or_request,
                 headers: dict = None,
                 data: dict = None,
                 params: dict = None,
                 cookies: dict = None
                 ) -> requests.Response:
        if isinstance(url_or_request, str):
            return self._get_page(url_or_request, headers, data, params, cookies)
        elif isinstance(url_or_request, requests.Request):
            return self.send_request(url_or_request)

    def send_request(self, req: requests.Request) -> requests.Response:
        prepped = self._session.prepare_request(req)

        resp = self._session.send(prepped)
                      # stream=stream,
                      # verify=verify,
                      # proxies=proxies,
                      # cert=cert,
                      # timeout=timeout
        return resp

    def _get_page(self,
                  url: str,
                  headers: dict = None,
                  data: dict = None,
                  params: dict = None,
                  cookies: dict = None,
                  stream: bool = False
                  ) -> requests.Response:
        request = {"url": url}
        if not headers:
            headers = self.general_headers
        else:
            headers = ChainMap(headers, self.general_headers)
        request["headers"] = headers

        if data:
            request["data"] = data
        if params:
            request["params"] = params
        if cookies:
            request["cookies"] = cookies
        if stream:
            request["stream"] = stream

        response = self._session.get(**request)
        return response
        # try:
        #     r = self._session.get(**request)
        # except requests.exceptions.RequestException as e:
        #     logging.error(e, url)
        #     raise e
        # else:
        #     if r.status_code >= 300:
        #         logging.error(f"STATUS CODE: {r.status_code} FOR PAGE: {url}")
        #     return r

    def _create_request(self,
                        method: str,
                        url: str,
                        headers: dict = None,
                        data: dict = None,
                        params: dict = None,
                        cookies=None
                        ) -> requests.Request:
        if headers:
            headers = ChainMap(self.general_headers, headers)
        else:
            headers = self.general_headers

        return requests.Request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            cookies=cookies
        )

    @retry.retry(requests.exceptions.RequestException, tries=3, delay=5)
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

        # Make request
        response = self._get_page(url=item.source, stream=True)

        if 200 <= response.status_code < 300:
            with open(file_path, 'wb') as f:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, f)

        if save_urls:
            with open(album_path / "urls.txt", "a") as f:
                f.write(item.source)
                f.write("\n")

    def update_cookies(self, cookies: dict, domain: str):
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain=domain)
