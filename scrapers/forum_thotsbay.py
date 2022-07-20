from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from .forum_thotsbay_auth import ForumThotsbayAuth
from utils import split_filename_ext
import logging
import re
import json

# Regex Patterns
PATTERN_THOTSBAYFORUM_THREAD = r"(?:https://)?forum\.thotsbay\.com/threads/[-\w\d\.]+/"


class ForumThotsbayCrawler(CrawlerBase, ForumThotsbayAuth):
    VALID_URL_RE = re.compile(r"")
    PROTOCOL = "https"
    DOMAIN = "forum.thotsbay.com"
    DESC = "Thotsbay Forum Thread"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://forum.thotsbay.com/threads/nataliexking-bbyluckie.12408/#post-337758",
        "https://forum.thotsbay.com/threads/abby-rao-abbyrao.10221/",
        "https://forum.thotsbay.com/threads/genesis-mia-lopez.24/",
        "https://forum.thotsbay.com/threads/angelie-dolly.13727/",
        "https://forum.thotsbay.com/threads/kelly-kay.14707/"
    ]

    def initialize(self):
        self.authorize()

    # Extractor method
    # def _extract_data(self, url):
    #     response = self._request_page(
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
