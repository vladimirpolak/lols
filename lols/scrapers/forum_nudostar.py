from .forum_nudostar_auth import ForumNudostarAuth
from ._scraper_base import ExtractorBase, CrawlerBase
from ..http.types import determine_content_type
from ..utils import slugify
from ..exceptions import ExtractionError

from typing import Union
import re

_CODENAME = "forum_nstar"

# Regex Patterns
PATTERN_NUDOSTARFORUM_THREAD = r"(?:https://)?nudostar\.com/forum/threads/([-\w\.]+)/?"
PATTERN_NUDOSTARFORUM_CONTENT = re.compile(
    r"((?:(?:https://)?nudostar\.com)?/forum/attachments/([-\w]+)-([a-zA-Z\d]+)\.\d+/?)"
)
PATTERN_NUDOSTARFORUM_THREAD_NEXTPAGE = r'rel="next"\s*href="(.*?)"'
PATTERN_NUDOSTARFORUM_THREADTITLE = r'<meta property="og:title" content="(?:OnlyFans - )?(?P<thread_title>.*?)"\s+/>'

Html = str
NextPage = str


def is_nudostar_domain(html) -> bool:
    p = re.compile(r'<meta\s+property="og:url"\s+content="(https://nudostar\.com/forum/threads/)')
    return bool(p.findall(html))


class ForumNudostarCrawler(CrawlerBase, ForumNudostarAuth):
    VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "nudostar.com"
    DESC = "Nudostar Forum Thread"
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

        if not self.THREAD_NAME:
            self.THREAD_NAME = slugify(self._extract_threadname(html), sep="_")
        next_page = self._extract_nextpage(html)

        return html, next_page

    def _extract_nextpage(self, html) -> Union[NextPage, None]:
        np_pattern = PATTERN_NUDOSTARFORUM_THREAD_NEXTPAGE
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path
        return None

    def _extract_threadname(self, html):
        match = re.search(PATTERN_NUDOSTARFORUM_THREADTITLE, html)
        if match:
            return match.group("thread_title")
        return None


class ForumNudostarContentExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_CONTENT)
    PROTOCOL = "https"
    DOMAIN = "nudostar.com"
    DESC = "Nudostar Forum Content"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        if url.startswith("https"):
            source = url
        else:
            source = self.base_url + url
        filename, extension = self._nudostar_process_filename(source)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    @classmethod
    def _nudostar_process_filename(cls, url):
        match = cls.VALID_URL_RE.match(url)
        if not match:
            raise ExtractionError(
                f"Failed to extract (filename, extension) from url: {url}, matching results = {match}"
            )
        filename = match.group(2)
        extension = f".{match.group(3)}"
        return filename, extension

    @classmethod
    def extract_from_html(cls, url, html):
        results = []
        if is_nudostar_domain(html) or url == "test":
            results.extend([data[0] for data in set(re.findall(cls.VALID_URL_RE, html))])
        return results

