from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json

# Constant URLs

# Regex Patterns
# -All regex patterns here
# -PATTERN_DOMAIN_TYPE
# -eg. PATTERN_CYBERDROP_ALBUM = r""
# -eg. PATTERN_BUNKR_IMAGE = r""


class DomainNameExtractor:
    NEXT_PAGE = None
    VALID_URL_RE = re.compile(r"")  # Regex pattern for url validation
    PROTOCOL = "https"  # http/s
    DOMAIN = "domain.com"
    DESC = "Simple Domain Description"
    # CONTENT_TYPE = None  # ITEM/ALBUM/THREAD  None if unknown
    SAMPLE_URLS = []

    # Extractor method
    # def _extract_data(self, url):
    #     response = self.request(
    #         url=url,
    #     )
    #
    #     self.add_item(
    #         content_type=content_type,
    #         filename=filename,
    #         extension=extension,
    #         source=source,
    #         album_title=album_title
    #     )

    # Extractor method only
    # @classmethod
    # def _extract_from_html(cls, html):
    #     return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

    # Crawler method only
    # def _crawl_link(self, url) -> html[str]:
    #     pass
