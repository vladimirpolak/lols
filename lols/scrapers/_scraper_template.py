from ..utils import split_filename_ext
from ..http.types import determine_content_type
from ._scraper_base import CrawlerBase, ExtractorBase
from ..exceptions import ExtractionError, ScraperInitError, ContentTypeError, ParsingError

from typing import Union, Tuple, Iterator

import logging
import re

_CODENAME = ''
# Constant URLs

# Regex Patterns


class DomainNameExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(r"")  # Regex pattern for url validation
    PROTOCOL = "https"
    DOMAIN = "domain.com"
    DESC = "Simple Domain Description"
    CODENAME = _CODENAME
    SAMPLE_URLS = []

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )

        # source =
        # filename =
        # extension =
        # content_type =

        # self.add_item(
        #     source=source,
        #     filename=filename,
        #     extension=extension,
        #     content_type=content_type,
        # )


Url = str
Html = str
NextPage = Union[str, None]


class DomainNameCrawler(CrawlerBase):
    VALID_URL_RE = re.compile(r"")  # Regex pattern for url validation
    PROTOCOL = "https"
    DOMAIN = "domain.com"
    DESC = "Simple Domain Description"
    CODENAME = _CODENAME
    SAMPLE_URLS = []

    def _crawl_link(self, url: str) -> Iterator[Tuple[Url, Html, NextPage]]:
        """
        Yield current url, it's html and the next possible page
        :param url: str
        :return: Iterator[Tuple[Url, Html, NextPage]]
        """
        while url:
            html, next_page = self._get_html_nextpage(url)
            yield url, html, next_page
            url = next_page

    def _get_html_nextpage(self, url) -> (Html, NextPage):
        """
        Extract html and next possible page of the url thread.
        :param url: str
        :return: (Html, NextPage)
        """
        pass
