from ..scrapers._scraper_base import CrawlerBase
from ..exceptions import ExtractionError
from .simpcity_auth import SimpCityAuth
from ..utils import slugify

from typing import Union

import re

_CODENAME = 'simpcity'

Html = str
NextPage = str

# Constant URLs

# Regex Patterns
PATTERN_SIMPCITY_THREAD = r"(?:https://)?simpcity\.su/threads/([-\w\.]+)/?"
PATTERN_SIMPCITY_THREAD_NEXTPAGE = r'rel="next"\s*href="(.*?)"'


class SimpCityCrawler(CrawlerBase, SimpCityAuth):
    VALID_URL_RE = re.compile(PATTERN_SIMPCITY_THREAD)  # Regex pattern for url validation
    PROTOCOL = "https"  # http/s
    DOMAIN = "simpcity.su"
    DESC = "Simpcity Forums"
    CODENAME = _CODENAME

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url: str):
        try:
            self.album_id = self.VALID_URL_RE.findall(url)[0]
        except IndexError:
            ExtractionError(f"Failed to extract album id from url: {url}")

        while url:
            html, next_page = self._get_html_nextpage(url)
            yield url, html, next_page
            url = next_page

    def _get_html_nextpage(self, url) -> (Html, NextPage):
        response = self.request(
            url=url,
        )
        html = response.text
        if self.username not in html:
            raise ExtractionError(f"Not authorized! (Most likely login session is expired.)")

        next_page = self._extract_nextpage(html)

        return html, next_page

    def _extract_nextpage(self, html) -> Union[NextPage, None]:
        np_pattern = PATTERN_SIMPCITY_THREAD_NEXTPAGE
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path
        return None
