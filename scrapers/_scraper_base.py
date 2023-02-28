import logging
import re
import requests
from typing import Dict
from downloader import Downloader, Item
from downloader.models import ContentType
from abc import abstractmethod
from exceptions import ExtractionError, ContentTypeError
from typing import List, Union
from enum import Enum, auto

Url = str
Html = str


class ScraperType(Enum):
    EXTRACTOR = auto()
    CRAWLER = auto()


class ScraperBase:
    ALL_ITEMS: List[Item] = []  # List of scraped items
    VALID_URL_RE: Union[re.Pattern, List]  # Regex pattern for url validation
    PROTOCOL: str  # http/s
    DOMAIN: str  # domain.com
    DESC: str  # scraper description
    SCRAPER_TYPE: ScraperType  # scraper type EXTRACTOR/CRAWLER
    CODENAME: str
    SAMPLE_URLS: List[str]  # list of example urls
    _downloader: Downloader

    def initialize(self):
        """
        Implemented in scraper subclasses.
        Used for authorization logic or any kind of pre-extract work needed to be done.
        """
        pass

    @classmethod
    def is_active(cls):
        return True

    @classmethod
    def is_suitable(cls, url) -> bool:
        """
        Determines if the scraper is suitable for extracting input link.
        """
        if isinstance(cls.VALID_URL_RE, re.Pattern):
            return bool(cls.VALID_URL_RE.match(url))
        elif isinstance(cls.VALID_URL_RE, list):
            return any(pattern.match(url) for pattern in cls.VALID_URL_RE)

    def set_http_api(self, downloader):
        self._downloader = downloader

    def request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Method for making Http requests."""
        return self._downloader.send_request(url, method, **kwargs)

    @property
    def base_url(self):
        return f"{self.PROTOCOL}://{self.DOMAIN}"

    @abstractmethod
    def extract_data(self, url: str):
        pass

    def __str__(self):
        return f"Scraper({self.base_url}, {self.DESC})"


class ExtractorBase(ScraperBase):
    SCRAPER_TYPE = ScraperType.EXTRACTOR

    def __init__(self, session: requests.Session):
        self._downloader = Downloader(session)
        self.initialize()

    def extract_data(self, url: str) -> List[Item]:
        self.ALL_ITEMS = []
        try:
            # _extract_data method is implemented in each extractor and adds target items into ALL_ITEMS list.
            self._extract_data(url)
        except (ExtractionError, ContentTypeError) as e:
            logging.error(e)

        if len(self.ALL_ITEMS) >= 1:
            logging.debug(f"{self.__class__.__name__} EXTRACTED {len(self.ALL_ITEMS)} ITEMS")
        return self.ALL_ITEMS

    def add_item(self,
                 source: str,
                 filename: str,
                 extension: str,
                 content_type: ContentType,
                 album_title: str = None,
                 headers: dict = None
                 ):
        """Used to add target item data to output list."""

        new_item = Item(
            source=source,
            filename=filename,
            extension=extension,
            content_type=content_type,
            album_title=album_title,
            headers=headers
        )
        logging.debug(f"{self.__class__.__name__} ADDED {new_item}")
        self.ALL_ITEMS.append(new_item)

    @abstractmethod
    def _extract_data(self, url: str):
        """This method is implemented in the subclass."""
        pass

    @classmethod
    def extract_from_html(cls, url: str, html: str) -> List[str]:
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]


class CrawlerBase(ScraperBase):
    """
    Crawler class is used to scrape multiple pages of thread/album
    and return raw html code, which will then be used to extract usable links
    from using 'extractor' classes.
    """
    NEXT_PAGE = None
    SCRAPER_TYPE = ScraperType.CRAWLER
    THREAD_NAME = ""

    def __init__(self, session: requests.Session, page_limit: int = 0):
        self._downloader = Downloader(session)
        self.initialize()
        self.page_limit = page_limit

    def extract_data(self, url: str) -> Dict[Url, Html]:
        return self._crawl_link(url)

    @abstractmethod
    def _crawl_link(self, url: str) -> dict:
        """This method is implemented in the subclass"""
        pass
