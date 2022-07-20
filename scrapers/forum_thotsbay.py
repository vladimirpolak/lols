from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from .forum_thotsbay_auth import ForumThotsbayAuth
from utils import split_filename_ext
from typing import Union
import logging
import re
import json

# Regex Patterns
PATTERN_THOTSBAYFORUM_THREAD = r"(?:https://)?forum\.thotsbay\.com/threads/([-\w\d\.]+)/"
PATTERN_THOTSBAYFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                        r'href="(/threads/{album_id}/page-\d+)"\s+' \
                                        r'class="[-\w\d\s]*pageNav-jump--next">'

Html = str
NextPage = str


class ForumThotsbayCrawler(CrawlerBase, ForumThotsbayAuth):
    VALID_URL_RE = re.compile(PATTERN_THOTSBAYFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "forum.thotsbay.com"
    DESC = "Thotsbay Forum Thread"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://forum.thotsbay.com/threads/nataliexking-bbyluckie.12408/#post-337758",
        "https://forum.thotsbay.com/threads/abby-rao-abbyrao.10221/",
        "https://forum.thotsbay.com/threads/genesis-mia-lopez.24/",
        "https://forum.thotsbay.com/threads/angelie-dolly.13727/",
        "https://forum.thotsbay.com/threads/riley-reid.9379/"
    ]

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url):
        try:
            self.album_id = self.VALID_URL_RE.findall(url)[0]
        except IndexError:
            ExtractionError(f"Failed to extract album id from url: {url}")

        all_html = ""
        while url:
            html, url = self._get_html_nextpage(url)
            all_html = all_html + html
        return all_html

    def _get_html_nextpage(self, url) -> (Html, NextPage):
        response = self._request_page(
            url=url,
        )
        html = response.text
        if self.username not in html:
            raise ExtractionError(f"Not authorized! (Most likely login session is expired.)")
        next_page = self._extract_nextpage(html)

        return html, next_page

    def _extract_nextpage(self, html) -> Union[NextPage, None]:
        np_pattern = PATTERN_THOTSBAYFORUM_THREAD_NEXTPAGE.format(album_id=self.album_id)
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path
        return None
