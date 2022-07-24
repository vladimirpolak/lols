from downloader.downloader import Downloader, Item
from typing import List, Union
import logging
import re


class ScraperBase:
    ALL_ITEMS: list = []
    VALID_URL_RE: Union[re.Pattern, List]  # Regex pattern for url validation
    PROTOCOL: str  # http/s
    DOMAIN: str  # domain.com
    DESC: str  # scraper description
    SCRAPER_TYPE: str
    SAMPLE_URLS: list
    _downloader: Downloader

    def initialize(self):
        """
        Implemented in scraper subclasses.
        Used for authorization logic or any kind of pre-extract work needed to be done.
        """
        pass

    @classmethod
    def is_suitable(cls, url):
        """
        Determines if the scraper is suitable for extracting input link.
        """
        if isinstance(cls.VALID_URL_RE, re.Pattern):
            return cls.VALID_URL_RE.match(url)
        elif isinstance(cls.VALID_URL_RE, list):
            return any(pattern.match(url) for pattern in cls.VALID_URL_RE)

    def set_downloader(self, downloader):
        self._downloader = downloader

    def request(self, url: str, method: str = 'GET', **kwargs):
        return self._downloader.send_request(url, method, **kwargs)

    def add_item(self,
                 content_type: str,
                 filename: str,
                 extension: str,
                 source: str,
                 album_title: str = None
                 ):

        new_item = Item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
            album_title=album_title
        )
        logging.debug(f"Adding Item: {new_item}")
        self.ALL_ITEMS.append(new_item)

    @property
    def base_url(self):
        return f"{self.PROTOCOL}://{self.DOMAIN}/"

    def extract_data(self, url: str):
        pass

    def __str__(self):
        return f"Scraper({self.base_url}, {self.DESC})"


class ExtractorBase(ScraperBase):
    SCRAPER_TYPE = "EXTRACTOR"

    def __init__(self, downloader=None):
        self._downloader = downloader
        self.initialize()

    def extract_data(self, url: str) -> List[Item]:
        self.ALL_ITEMS = []
        self._extract_data(url)

        if len(self.ALL_ITEMS) > 1:
            logging.debug(f"NUMBER OF DATA: {len(self.ALL_ITEMS)}")
        return self.ALL_ITEMS

    def _extract_data(self, url: str):
        """This method is implemented in the subclass"""
        pass

    @classmethod
    def _extract_from_html(cls, html):
        """This method is implemented in the subclass"""
        pass


class CrawlerBase(ScraperBase):
    """
    Crawler class is used to scrape multiple pages of thread/album
    and return raw html code, which will then be used to extract usable links
    from using 'extractor' classes.
    """
    NEXT_PAGE = None
    SCRAPER_TYPE = "CRAWLER"

    def __init__(self, downloader=None):
        self._downloader = downloader
        self.initialize()

    def extract_data(self, url: str) -> str:
        return self._crawl_link(url)

    def _crawl_link(self, url: str) -> str:
        """This method is implemented in the subclass"""
        pass
