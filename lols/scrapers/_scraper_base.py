from ..http import HttpClient, Item
from ..http.models import ContentType
from ..exceptions import ExtractionError, ContentTypeError, PasswordRequired

from abc import abstractmethod
from typing import List, Union, Dict, Iterator, Tuple
from enum import Enum, auto

import logging
import re
import requests


class ScraperType(Enum):
    EXTRACTOR = auto()
    CRAWLER = auto()


class ScraperBase:
    VALID_URL_RE: Union[re.Pattern, List]  # Regex pattern for url validation
    PROTOCOL: str  # http/s
    DOMAIN: str  # domain.com
    DESC: str  # scraper description
    SCRAPER_TYPE: ScraperType  # scraper type EXTRACTOR/CRAWLER
    CODENAME: str
    TESTS: dict = dict()
    SAMPLE_URLS: List[str] = []  # list of example urls
    _http: HttpClient

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

    def set_http_api(self, client: HttpClient):
        self._http = client

    def request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """Method for making Http requests."""
        return self._http.send_request(url, method, **kwargs)

    @property
    def base_url(self):
        return f"{self.PROTOCOL}://{self.DOMAIN}"

    @abstractmethod
    def extract_data(self, url: str):
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.base_url}, {self.DESC})"


class ExtractorBase(ScraperBase):
    ALL_ITEMS: List[Item] = []  # List of scraped items
    SCRAPER_TYPE = ScraperType.EXTRACTOR

    def __init__(self, session: requests.Session):
        self._http = HttpClient(session)
        self.initialize()

    def extract_data(self, url: str) -> List[Item]:
        self.ALL_ITEMS = []
        try:
            # _extract_data method is implemented in each extractor and adds target items into ALL_ITEMS list.
            self._extract_data(url)
        except (ExtractionError, ContentTypeError) as e:
            logging.error(e)
        except PasswordRequired as e:
            logging.error(e)
            # TODO Handle password

        if self.ALL_ITEMS:
            logging.debug(f"{self.__class__.__name__} EXTRACTED {len(self.ALL_ITEMS)} ITEMS")
        return self.ALL_ITEMS

    def add_item(self,
                 source: str,
                 filename: str,
                 extension: str,
                 content_type: ContentType,
                 **kwargs):
        """
           Add target item data to the output list.

           :param source: The source link.
           :param filename: Name of the file to be added.
           :param extension: The file extension.
           :param content_type: The type of content in the item.
           :param album_title: (optional) The title of the album the item belongs to.
           :param headers: (optional) A dictionary of HTTP headers to include in the request.
           :param req_kwargs: (optional) A dictionary of additional request parameters.
           :return: None

           Usage:
               To add an item to the output list, call this function with the required parameters.
               You can also include any additional parameters as keyword arguments.
        """

        new_item = Item(
            source=source,
            filename=filename,
            extension=extension,
            content_type=content_type,
            album_title=kwargs.pop("album_title", None),
            headers=kwargs.pop("headers", None),
            req_kwargs=kwargs.pop("req_kwargs", None)
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


Url = str
Html = str
NextPage = Union[str, None]


class CrawlerBase(ScraperBase):
    """
    Crawler class is used to scrape multiple pages of thread/album
    and return raw html code, which will then be used to extract usable links
    from using 'extractor' classes.
    """
    SCRAPER_TYPE = ScraperType.CRAWLER
    THREAD_NAME = ""

    def __init__(self, session: requests.Session, page_limit: int = 0):
        self._http = HttpClient(session)
        self.initialize()
        self.page_limit = page_limit

    def extract_data(self, url: str) -> Dict[Url, Html]:
        output = dict()
        logging.info(f"Crawling {url}...")
        for url, html, next_page in self._crawl_link(url):
            logging.debug(f"Next page: {next_page}")
            output[url] = html

            # logging.debug(f"Page Limit: {self.page_limit}, Current Page Count: {len(output)}")
            # logging.debug(f"Condition: {bool(self.page_limit and (len(output) == self.page_limit))}")
            if self.page_limit and len(output) == self.page_limit:
                break
        return output

    @abstractmethod
    def _crawl_link(self, url: str) -> Iterator[Tuple[Url, Html, NextPage]]:
        """This method is implemented in the subclass"""
        pass
