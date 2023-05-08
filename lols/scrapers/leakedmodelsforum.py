from .leakedmodelsforum_auth import LeakedmodelsForumAuth
from ._scraper_base import ExtractorBase, CrawlerBase
from ..http.types import determine_content_type, vid_extensions
from ..utils import split_filename_ext
from ..exceptions import ExtractionError

from typing import Union
import re

_CODENAME = "forum_lm"

# Regex Patterns
PATTERN_LEAKEDMODELSFORUM_THREAD = r"(?:https://)?leakedmodels\.com/forum/threads/([-\w\.]+)/?"
PATTERN_LEAKEDMODELSFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                        r'href="(/forum/threads/{album_id}/page-\d+)"\s+' \
                                        r'class="[-\w\d\s]*pageNav-jump--next">'
PATTERN_LEAKEDMODELSFORUM_IMAGE = re.compile(r"((?:(?:https://)?leakedmodels\.com)?/forum/attachments/([-\d\w]+)-([a-zA-Z]+)\.\d+/?)")
PATTERN_LEAKEDMODELSFORUM_VIDEO = re.compile(rf"(?:https://)?cdn\.leakedmodels\.com/forum/data/video/\d+/[-\w]+(?:{'|'.join(vid_extensions)})")
PATTERN_LEAKEDMODELSFORUM_THREADTITLE = r'<h1 class="p-title-value"(?:.)*</span>([-\w\s]+)</h1>'

Html = str
NextPage = str


def is_leakedmodels_domain(html) -> bool:
    p = re.compile(r'<meta\s+property="og:url"\s+content="(https://leakedmodels\.com/forum/threads/)')
    return bool(p.findall(html))


class LeakedmodelsForumCrawler(CrawlerBase, LeakedmodelsForumAuth):
    VALID_URL_RE = re.compile(PATTERN_LEAKEDMODELSFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "leakedmodels.com"
    DESC = "Leakedmodels Forum Thread"
    CODENAME = _CODENAME

    def initialize(self):
        self.authorize()

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
            self.THREAD_NAME = self._extract_threadname(html)
            print(self.THREAD_NAME)
        next_page = self._extract_nextpage(html)

        return html, next_page

    def _extract_nextpage(self, html) -> Union[NextPage, None]:
        np_pattern = PATTERN_LEAKEDMODELSFORUM_THREAD_NEXTPAGE.format(album_id=self.album_id)
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path
        return None

    def _extract_threadname(self, html):
        p = re.compile(PATTERN_LEAKEDMODELSFORUM_THREADTITLE)
        results = p.findall(html)
        if results and (len(results) > 1):
            return results[1]
        elif results and(len(results) == 1):
            return results[0]


class LeakedmodelsForumImageExtractor(ExtractorBase, LeakedmodelsForumAuth):
    VALID_URL_RE = re.compile(PATTERN_LEAKEDMODELSFORUM_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "leakedmodels.com"
    DESC = "Leakedmodels Forum Image"
    CODENAME = _CODENAME

    def initialize(self):
        self.authorize()

    def _extract_data(self, url):
        source = self.base_url + url
        filename, extension = self._leakedmodels_process_filename(source)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    @classmethod
    def _leakedmodels_process_filename(cls, url):
        match = cls.VALID_URL_RE.match(url)
        if not match:
            raise ExtractionError(
                f"Failed to extract (filename, extension) from url: {url}, matching results = "
            )
        filename = match.group(2)
        extension = f".{match.group(3)}"
        return filename, extension

    @classmethod
    def extract_from_html(cls, url, html):
        results = []
        if is_leakedmodels_domain(html) or url == "test":
            results.extend([data[0] for data in set(re.findall(cls.VALID_URL_RE, html))])
        return results


class LeakedmodelsForumVideoExtractor(ExtractorBase, LeakedmodelsForumAuth):
    VALID_URL_RE = re.compile(PATTERN_LEAKEDMODELSFORUM_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "leakedmodels.com"
    DESC = "Leakedmodels Forum Video"
    CODENAME = _CODENAME

    def initialize(self):
        self.authorize()

    def _extract_data(self, url):
        if url.endswith("/"):
            file_w_ext = url[:-1].split("/")[-1]
        else:
            file_w_ext = url.split("/")[-1]

        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )
