from ._scraper_base import CrawlerBase
from typing import Union
import re

_CODENAME = "planets"

# Regex Patterns
PATTERN_PLANETSUZY_THREAD = r"((?:https?://)?(?:www\.)?planetsuzy\.org(/t\d+-[-\w]+(?:\.html)?))"
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
    CODENAME = _CODENAME
    SAMPLE_URLS = [
        "http://planetsuzy.org/t967900-daisy-keech.html",
        "http://www.planetsuzy.org/t977950-niece-waidhofer.html",
        "http://www.planetsuzy.org/t712898-kindly-myers.html"
    ]

    def _crawl_link(self, url):
        # Used for creating next page url
        self.thread_path = self.VALID_URL_RE.match(url).group(2)

        output = dict()
        while url:
            html, next_page = self._get_html_nextpage(url)
            output[url] = html
            url = next_page
        return output

    def _get_page_html(self, url) -> (Html, NextPageUrl):
        response = self.request(
            url=url,
        )

        html = response.text
        if not self.THREAD_NAME:
            self.THREAD_NAME = self._extract_model_name(html)
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

    def _extract_model_name(self, html) -> Union[str, None]:
        pattern = re.compile(r"<title>([\d\w\s]+) - Free Porn & Adult Videos Forum</title>")
        results = pattern.findall(html)
        if results:
            album_title = results[0].strip()
            return album_title
        return None
