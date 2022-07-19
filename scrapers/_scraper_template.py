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


class DomainNameExtractor:
    NEXT_PAGE = None
    VALID_URL_RE = re.compile(r"")  # Regex pattern for url validation
    PROTOCOL = "https"  # http/s
    DOMAIN = "domain.com"
    DESC = "Simple Domain Description"
    # CONTENT_TYPE = None  # ITEM/ALBUM/THREAD  None if unknown
    SAMPLE_URLS = []

    def _extract_data(self, url):
        # response = self._request_page(
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
