from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import (ExtractionError,
                        GoFileStatusUnknownError)
from utils import split_filename_ext
from .gofile_auth import GoFileAuth
from hashlib import sha256
import logging
import re

# Constant URLs
URL_GOFILE_FOLDER = "https://gofile.io/d/"
URL_GOFILE_CONTENT = "https://api.gofile.io/getContent"

# Regex Patterns
PATTERN_GOFILE_ALBUM = r"((?:https?://)?gofile\.io/d/\w+)"

# GoFile request headers
gofile_headers = {
    "origin": "https://gofile.io",
    "referer": "https://gofile.io/"
}


def gf_query_params(album_id, token, password: str = None) -> dict:
    """Query parameters for GoFile 'getContent' URL."""
    query_params = {
        "contentId": album_id,
        "token": token,
        "websiteToken": "12345"
    }
    if password:
        query_params["password"] = sha256(password.encode()).hexdigest()
        query_params["cache"] = "true"
    return query_params


class Status:
    """Class that evaluates the Gofile response's status messages."""
    def __init__(self, status: str):
        self.status = status
    @property
    def success(self) -> bool:
        return self.status == "ok"
    @property
    def password_required(self) -> bool:
        return self.status == "error-passwordRequired"
    @property
    def file_not_found(self) -> bool:
        return self.status == "error-notFound"


class GoFileFolderExtractor(ExtractorBase, GoFileAuth):
    VALID_URL_RE = re.compile(PATTERN_GOFILE_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "gofile.io"
    DESC = "GoFile Hosting Directory"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://gofile.io/d/eG1URC",  # 1 video
        "https://gofile.io/d/RPoxUP",  # Multiple directories
        "https://gofile.io/d/rhjWaX",  # 1 archive
        "https://gofile.io/d/O407z8",  # Images and Videos
        "https://gofile.io/d/rtHOqG",  # 1 video
    ]

    def initialize(self):
        # Authorize here
        self.authorize()

    def _extract_data(self, url, password: str = None) -> None:
        """Recursively scrapes the album if it contains any subfolders."""
        # GoFile Folder ID from url
        album_id = url.split("/")[-1]

        # Generate query parameters
        params = gf_query_params(album_id, self.ACCESS_TOKEN, password)

        # Request a page
        response = self.request(
            url=URL_GOFILE_CONTENT,
            headers=gofile_headers,
            params=params
        )

        # TODO This will have to be cleaned up somehow
        if not response.status_code == 200:
            raise ExtractionError(
                f"Failed to retrieve GoFile webpage, "
                f"response status code: {response.status_code}"
            )

        json = response.json()
        album_status = Status(json["status"])

        # TODO I'm not really satisfied with this bit,
        #  status validation and album_data extraction should preferably
        #  be two separate functions/methods. It is what it is, for now.
        album_data = {}
        if album_status.success:
            album_data = json["data"]["contents"]
        elif album_status.file_not_found:
            logging.debug(f"Gofile 404: {url}")
        elif album_status.password_required:
            logging.debug(f"GoFile Password-Required: {url}")
            self._extract_data(url=url, password=input(f"Enter password for '{url}': "))
        else:
            raise GoFileStatusUnknownError(f"GoFile unknown status: {json}")

        if album_data:
            self._parse_album_data(album_data)

    def _parse_album_data(self, album_data: dict) -> None:
        for item_id, item_info in album_data.items():
            file_type = item_info["type"]

            # If current album contains another folder:
            if file_type == "folder":
                folder_code = item_info["code"]
                folder_url = URL_GOFILE_FOLDER + folder_code

                # Extract subfolder (Recursive manner)
                self._extract_data(url=folder_url)

            # Else Parse the item
            elif file_type == "file":
                self.add_item(**self._parse_album_file(item_info))

    def _parse_album_file(self, item_info: dict) -> dict:
        source = item_info["link"]
        file_w_extension = item_info["name"]
        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type_(extension)
        return {
            'source': source,
            'filename': filename,
            'extension': extension,
            'content_type': content_type
        }

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
