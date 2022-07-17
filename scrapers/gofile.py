from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
from datetime import datetime
import logging
import re

GOFILE_TOKEN_REQ_URL = "https://api.gofile.io/createAccount"
GOFILE_CONTENT_URL = "https://api.gofile.io/getContent"

PATTERN_GOFILE_ALBUM = r"((?:https?://)?gofile\.io/d/\w+)"


class GoFileAuth:
    """GoFile Authorization mixin."""
    ACCESS_TOKEN = ""

    def login(self):
        auth_data = config.load_config(self.DOMAIN)

        if not auth_data:
            self._create_login()
            return self.ACCESS_TOKEN

        self.ACCESS_TOKEN = auth_data["token"]
        date_created = auth_data["created_at"]

        if not self.token_is_valid(date_created):
            self._create_login()
        return self.ACCESS_TOKEN

    def _create_login(self):
        self.ACCESS_TOKEN = self.request_token()

        auth_data = {
            "token": self.ACCESS_TOKEN
        }
        config.save_config(
            self.DOMAIN,
            auth_data
        )

    def request_token(self):
        """Method for requesting new GoFile access token."""
        logging.debug("Requesting GoFile access token.")

        # Create guest account URL
        req = self._downloader._create_request(method='GET', url=GOFILE_TOKEN_REQ_URL)
        r = self._send_request_object(req)

        if r.status_code == 200:

            json = r.json()
            if json["status"] == "ok":
                # Extract access token
                token = json["data"]["token"]

                logging.debug(f"New GoFile token: {token}")
                return token
            raise ScraperInitError(f"Failed to retrieve access token from data: {json}")
        logging.debug(r)
        raise ScraperInitError(f"Failed to retrieve access token, response code: {r.status_code}")

    @classmethod
    def token_is_valid(cls, date):
        """Invalid token if current is older than 24 hours."""
        difference = datetime.now() - date
        return difference.days == 0


def gf_query_params(album_id, token):
    """Query parameters for GoFile 'getContent' URL."""
    query_params = {
        "contentId": album_id,
        "token": token,
        "websiteToken": "12345"
    }
    return query_params


class GoFileFolderExtractor(ExtractorBase, GoFileAuth):
    VALID_URL_RE = re.compile(PATTERN_GOFILE_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "gofile.io"
    DESC = "GoFile File Storage"
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
        self.login()

    def _extract_data(self, url):
        """Recursively scrapes the album if it contains any subfolders."""
        # Album ID from url
        album_id = url.split("/")[-1]

        # Generate query parameters
        params = gf_query_params(album_id, self.ACCESS_TOKEN)

        # Additional headers
        gofile_headers = {
            "origin": "https://gofile.io",
            "referer": "https://gofile.io/"
        }

        # Request a page
        r = self._request_page(
            url=GOFILE_CONTENT_URL,
            headers=gofile_headers,
            params=params
        )

        if not r.status_code == 200:
            raise ExtractionError(
                f"Failed to retrieve gallery data.\n"
                f"Response status code: {r.status_code}"
            )

        json = r.json()

        if json["status"] == "ok":
            pass
        elif json["status"] == "error-notFound":
            # Exception: GoFile ERROR: {'status': 'error-notFound', 'data': {}}
            logging.debug(f"GoFile Error, file not found. {url}")
        elif json["status"] == "error-passwordRequired":
            logging.debug(f"PASSWORD REQUIRED FOR: {url}")
        else:
            raise ExtractionError(f"GoFile ERROR: {json}")

        album_data = json["data"]["contents"]

        # Album content extraction
        for item_id, item_info in album_data.items():
            file_type = item_info["type"]

            # If current album contains another folder:
            if file_type == "folder":
                folder_code = item_info["code"]
                folder_url = f"https://gofile.io/d/{folder_code}"

                # Extract subfolder (Recursive manner)
                self._extract_data(url=folder_url)

            elif file_type == "file":
                # {
                #     'id': 'd1ddff5d-01eb-4aff-a7d2-0851f04742a6',
                #     'type': 'file',
                #     'name': 'Liya Silver on Twitter Stuck in elevator with my girlfriend .mp4',
                #     'parentFolder': '680abd8a-5b0f-4bfb-be1f-c8fac71d2c9f',
                #     'createTime': 1637068145,
                #     'size': 4233682,
                #     'downloadCount': 2039,
                #     'md5': '3d5b5cd96631af7a4cf5795f6e82bd14',
                #     'mimetype': 'video/mp4',
                #     'viruses': [
                #
                #     ],
                #     'serverChoosen': 'store3',
                #     'directLink': 'https://store3.gofile.io/download/direct/fname.mp4',
                #     'link': 'https://store3.gofile.io/download/fname.mp4'
                # }
                source = item_info["link"]
                file_w_extension = item_info["name"]
                filename, extension = split_filename_ext(file_w_extension)
                content_type = determine_content_type_(extension)

                self.add_item(
                    source=source,
                    filename=filename,
                    extension=extension,
                    content_type=content_type
                )
