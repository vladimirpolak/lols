from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from .forum_nudostar_auth import ForumNudostarAuth
from typing import Union
import re

# Regex Patterns
PATTERN_NUDOSTARFORUM_THREAD = r"(?:https://)?nudostar\.com/forum/threads/([-\w\d\.]+)/?"
PATTERN_NUDOSTARFORUM_IMAGE = r"((?:https://)?nudostar\.com/forum/attachments/([-\d\w]+)-([a-zA-Z]+)\.\d+/)"
PATTERN_NUDOSTARFORUM_THREAD_NEXTPAGE = r'rel="next"\s*href="(.*?)"'

Html = str
NextPage = str


class ForumNudostarCrawler(CrawlerBase, ForumNudostarAuth):
    VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "nudostar.com"
    DESC = "Nudostar Forum Thread"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://nudostar.com/forum/threads/ck0rf.34621/",
        "https://nudostar.com/forum/threads/sierra-skye.55671/",
        "https://nudostar.com/forum/threads/h-nn-howo-ae-thetic-11yhannah.41934/",
        "https://nudostar.com/forum/threads/irenablond-irena-yam.36789/",
        "https://nudostar.com/forum/threads/cshepx.6437/"
    ]

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url):
        try:
            self.album_id = self.VALID_URL_RE.findall(url)[0]
        except IndexError:
            ExtractionError(f"Failed to extract album id from url: {url}")
        else:
            print(self.album_id)

        output = dict()

        while url:
            html, next_page = self._get_html_nextpage(url)
            output[url] = html
            url = next_page

        return output

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
        print(next_page)

        return html, next_page

    def _extract_nextpage(self, html) -> Union[NextPage, None]:
        np_pattern = PATTERN_NUDOSTARFORUM_THREAD_NEXTPAGE
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path[1:]
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


class ForumNudostarImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "nudostar.com"
    DESC = "Nudostar Forum Image"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://nudostar.com/forum/attachments/rn1yfyd2og471-jpg.895744/",
        "https://nudostar.com/forum/attachments/f6b2f53d-93ce-46e0-a4af-051f52552b92-jpeg.895754/"
    ]

    def _extract_data(self, url):
        filename, extension = self._nudostar_process_filename(url)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )

    def _nudostar_process_filename(self, url):
        results = self.VALID_URL_RE.findall(url)
        if not results:
            print(results)
            raise ExtractionError(f"Failed to extract filename, extension from url: {url}")
        match = results[0]
        filename = match[1]
        extension = f".{match[2]}"
        return filename, extension

    @classmethod
    def extract_from_html(cls, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]

