from ._scraper_base import CrawlerBase
from typing import Union
import re

# Regex Patterns
PATTERN_PLANETSUZY_THREAD = r"((?:https?://)?(?:www\.)?planetsuzy\.org/(t\d+-[-\w\d]+(?:\.html)?))"
PATTERN_PLANETSUZY_THREAD_NEXTPAGE = r'<a\s' \
                                     r'rel="next"\s' \
                                     r'class="smallfont"\s' \
                                     r'href="(.*?)"'
Html = str
NextPageUrl = str


class PlanetSuzyCrawler(CrawlerBase):
    NEXT_PAGE = None
    VALID_URL_RE = re.compile(PATTERN_PLANETSUZY_THREAD)
    PROTOCOL = "http"
    DOMAIN = "planetsuzy.org"
    DESC = "PlanetSuzy Forum Thread"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "http://planetsuzy.org/t967900-daisy-keech.html",
        "http://www.planetsuzy.org/t977950-niece-waidhofer.html",
        "http://www.planetsuzy.org/t712898-kindly-myers.html"
    ]

    def _crawl_link(self, url):
        # Used for creating next page url
        self.thread_path = self.VALID_URL_RE.match(url).group(2)

        all_html = ""

        while url:
            page_html, url = self._get_page_html(url)
            all_html = all_html + page_html
        return all_html

    def _get_page_html(self, url) -> (Html, NextPageUrl):
        response = self._request_page(
            url=url,
        )

        html = response.text
        next_page_url = self._get_next_page(html)

        return html, next_page_url

    def _get_next_page(self, html) -> Union[NextPageUrl, None]:
        match = re.search(PATTERN_PLANETSUZY_THREAD_NEXTPAGE, html)
        if match:
            np_url = match.group(1)
            if np_url.startswith("showthread"):
                next_page_number = np_url.split("page=")[-1]
                next_page_url = self.base_url + self.thread_path.replace(
                    "-", "-p{}-".format(next_page_number), 1
                )
            else:
                next_page_url = self.base_url + np_url
            return next_page_url
        return None


