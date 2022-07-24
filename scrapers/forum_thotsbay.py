from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from .forum_thotsbay_auth import ForumThotsbayAuth
from typing import Union
import re

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
    CONTENT_TYPE = "THREAD"
    MODEL_NAME = ""
    SAMPLE_URLS = [
        "https://forum.thotsbay.com/threads/nataliexking-bbyluckie.12408/",
        "https://forum.thotsbay.com/threads/abby-rao-abbyrao.10221/",
        "https://forum.thotsbay.com/threads/genesis-mia-lopez.24/",
        "https://forum.thotsbay.com/threads/angelie-dolly.13727/",
        "https://forum.thotsbay.com/threads/riley-reid.9379/",
        "https://forum.thotsbay.com/threads/ladyxzero.14241/",
        "https://forum.thotsbay.com/threads/ines-helene.11402/",
        "https://forum.thotsbay.com/threads/lupeandmicha.11155"
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
        response = self.request(
            url=url,
        )
        html = response.text
        if self.username not in html:
            raise ExtractionError(f"Not authorized! (Most likely login session is expired.)")
        if not self.MODEL_NAME:
            self.MODEL_NAME = self._extract_model_name(html)
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
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://forum.thotsbay.com/attachments/yana-demeester_103986718_551074562441545_7929775646538835571_n-jpg.15820/",
        "https://forum.thotsbay.com/attachments/2595x3461_7052232608779ce8b472fbc554bab754-jpg.48009/",
        "https://forum.thotsbay.com/attachments/3840x2880_b8c756e2f4d095510a6ecc39c569d16e-jpg.48004/",
        "https://forum.thotsbay.com/attachments/yana-demeester_236183838_551266026063915_5728592508069254494_n-jpg.48013/"
    ]

    def _extract_data(self, url):
        filename, extension = self._thotsbay_process_filename(url)
        content_type = determine_content_type_(extension)

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
    def _extract_from_html(cls, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]

