from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from utils import split_filename_ext
import logging
import re
import json

# Constant URLs
API_LINK = "https://pixeldrain.com/api"
API_FILE_LINK = "https://pixeldrain.com/api/file/"

# Regex Patterns
PATTERN_PIXELDRAIN_ALBUM = r"((?:https?://)?pixeldrain\.com/(?:l|u)/\w+)"
PATTERN_PIXELDRAIN_ALBUM_DATA = r"window\.viewer_data = ({.*});"


class PixelDrainAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_PIXELDRAIN_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "pixeldrain.com"
    DESC = "Pixeldrain Image Storage"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://pixeldrain.com/l/YqPurHqs",
        "https://pixeldrain.com/l/TMUr8i2C"
    ]

    def _extract_data(self, url):
        response = self._request_page(
            url=url,
        )
        html = response.text

        try:
            data = self._extract_album_data(html)
        except Exception:
            raise ExtractionError(
                f"\n{url}\n"
                f"Failed to extract album data."
            )
        album_id = data["id"]

        try:
            files = data["files"]
        except KeyError:
            files = [data]

        for item in files:
            file_w_extension = item["name"]
            filename, extension = split_filename_ext(file_w_extension)
            source = API_FILE_LINK + item["id"]
            content_type = determine_content_type_(extension)

            self.add_item(
                content_type=content_type,
                filename=filename,
                extension=extension,
                source=source,
                album_title=album_id
            )

    def _extract_album_data(self, html) -> dict:
        pattern = re.compile(PATTERN_PIXELDRAIN_ALBUM_DATA)

        match = re.search(pattern, html)

        data_str = match.group(1)

        # {'type': 'list', 'api_response': { 'files': [data_objects]}
        data = json.loads(data_str)
        logging.debug(f"ALBUM DATA: {data}")
        return data["api_response"]

    @classmethod
    def _extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

