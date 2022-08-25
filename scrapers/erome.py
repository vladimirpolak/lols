from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json

PATTERN_EROME_ALBUM = r"(?:https://)?(www\.)erome\.com/a/\w+"


class EromeAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_EROME_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "erome.com"
    DESC = "Erome Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://www.erome.com/a/69MH41fn",
        "https://www.erome.com/a/srArB7Yt"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )

        # self.add_item(
        #     content_type=content_type,
        #     filename=filename,
        #     extension=extension,
        #     source=source,
        #     album_title=album_title
        # )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
