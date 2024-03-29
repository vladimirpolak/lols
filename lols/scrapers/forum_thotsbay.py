from .forum_thotsbay_auth import ForumThotsbayAuth
from ._scraper_base import ExtractorBase, CrawlerBase
from ..http.types import determine_content_type
from ..exceptions import ExtractionError

from typing import Union
import re

_CODENAME = "forum_tbay"

# Regex Patterns
PATTERN_THOTSBAYFORUM_THREAD = r"(?:https://)?forum\.thotsbay\.com/threads/([-\w\d\.]+)/?"
PATTERN_THOTSBAYFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                        r'href="(/threads/{album_id}/page-\d+)"\s+' \
                                        r'class="[-\w\d\s]*pageNav-jump--next">'
PATTERN_THOTSBAYFORUM_IMAGE = r"((?:https://)?forum\.thotsbay\.com/attachments/([-\d\w]+)-([a-zA-Z]+)\.\d+/)"

Html = str
NextPage = str


class ForumThotsbayCrawler(CrawlerBase, ForumThotsbayAuth):
    VALID_URL_RE = re.compile(PATTERN_THOTSBAYFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "forum.thotsbay.com"
    DESC = "Thotsbay Forum Thread"
    CODENAME = _CODENAME
    SAMPLE_URLS = []

    @classmethod
    def is_active(cls):
        return False

    def initialize(self):
        raise NotImplementedError("Site is shut down permanently.")
        # self.authorize()

    def _crawl_link(self, url):
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
        if not self.THREAD_NAME:
            self.THREAD_NAME = self._extract_model_name(html)
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

    def _extract_model_name(self, html):
        patterns = (
            re.compile(r"https://(?:www)?\.instagram\.com/([-\d\w.]+)/?"),
            re.compile(r"https://(?:www)?onlyfans\.com/([-\d\w.]+)/?"),
            re.compile(r"https://(?:www)?fansly\.com/([-\d\w.]+)/?")
        )
        for p in patterns:
            results = p.findall(html)
            if results and (len(results) > 1):
                return results[1]
            elif results and(len(results) == 1):
                return results[0]


class ForumThotsbayImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_THOTSBAYFORUM_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "forum.thotsbay.com"
    DESC = "Thotsbay Forum Image"
    CODENAME = _CODENAME
    SAMPLE_URLS = []

    @classmethod
    def is_active(cls):
        return False

    def _extract_data(self, url):
        filename, extension = self._thotsbay_process_filename(url)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )

    def _thotsbay_process_filename(self, url):
        results = self.VALID_URL_RE.findall(url)
        if not results:
            print(results)
            raise ExtractionError(f"Failed to extract filename, extension from url: {url}")
        match = results[0]
        filename = match[1]
        extension = f".{match[2]}"
        return filename, extension

    @classmethod
    def extract_from_html(cls, url, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]
