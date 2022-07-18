from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json

# All constant URLs here

# All regex patterns here
# PATTERN_DOMAIN_TYPE
# eg. PATTERN_CYBERDROP_ALBUM
# eg. PATTERN_BUNKR_IMAGE
PATTERN_PIXL_ALBUM = r"(?:https?://)?pixl\.is/album/[\w\d-.]+"


class PixlAlbumExtractor:
    VALID_URL_RE = re.compile(PATTERN_PIXL_ALBUM)  # Regex pattern for url validation
    PROTOCOL = "https"  # http/s
    DOMAIN = "pixl.is"
    DESC = "Pixl Image Hosting"
    # CONTENT_TYPE = None  # ITEM/ALBUM/THREAD  None if unknown
    SAMPLE_URLS = [
        "https://pixl.is/album/my-1st-album.KISg3",
    ]

    def _extract_data(self, url):
        # html = self._request_page(
        #     url=url,
        # )

        # self.add_item(
        #     content_type=content_type,
        #     filename=filename,
        #     extension=extension,
        #     source=source,
        #     album_title=album_title
        # )
        pass
