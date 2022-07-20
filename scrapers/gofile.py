from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from utils import split_filename_ext
from .gofile_auth import GoFileAuth
import logging
import re

# Constant URLs
GOFILE_CONTENT_URL = "https://api.gofile.io/getContent"

# Regex Patterns
PATTERN_GOFILE_ALBUM = r"((?:https?://)?gofile\.io/d/\w+)"


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
        self.authorize()

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
