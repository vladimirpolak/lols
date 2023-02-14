from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type, vid_extensions
from utils import split_filename_ext
from exceptions import ExtractionError
from .leakedmodelsforum_auth import LeakedmodelsForumAuth
from typing import Union
import re

# Regex Patterns
PATTERN_LEAKEDMODELSFORUM_THREAD = r"(?:https://)?leakedmodels\.com/forum/threads/([-\w\.]+)/?"
PATTERN_LEAKEDMODELSFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                        r'href="(/forum/threads/{album_id}/page-\d+)"\s+' \
                                        r'class="[-\w\d\s]*pageNav-jump--next">'
PATTERN_LEAKEDMODELSFORUM_IMAGE = r"(?:(?:https://)?leakedmodels\.com)?/(forum/attachments/([-\d\w]+)-([a-zA-Z]+)\.\d+/?)"
PATTERN_LEAKEDMODELSFORUM_VIDEO = rf"(?:https://)?cdn\.leakedmodels\.com/forum/data/video/\d+/[-\w]+(?:{'|'.join(vid_extensions)})"
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
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://leakedmodels.com/forum/threads/jasmin-heaney-irish-girl.5590/",
        "https://leakedmodels.com/forum/threads/my-h-yden.12432/",
        "https://leakedmodels.com/forum/threads/angelsweetsxo.15195/",
        "https://leakedmodels.com/forum/threads/hanalexiis.2209/",
        "https://leakedmodels.com/forum/threads/deanadelrey.15518/"
    ]

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url):
        try:
            self.album_id = self.VALID_URL_RE.findall(url)[0]
        except IndexError:
            ExtractionError(f"Failed to extract album id from url: {url}")

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
                return self.base_url + url_path[1:]
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
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://leakedmodels.com/forum/attachments/1125x1437_6cf8f45d57355a1d832ce35be1dadd1f-jpg.108958/",
        "https://leakedmodels.com/forum/attachments/1125x2436_7d0569179cc3b4abd37bd7acd1c1abb7-jpg.108962/",
        "https://leakedmodels.com/forum/attachments/1536x2048_abe5e130e4079c086dce89863359983d-jpg.108976/",
        "https://leakedmodels.com/forum/attachments/1620x2160_6fc9418de673080321a6e6265b69c5a169178-jpg.108987/",
        "https://leakedmodels.com/forum/attachments/1620x2160_38e85b35a1bfa564af04d8768758590d4382945d9a69bf45134-jpg.108994/",
        "https://leakedmodels.com/forum/attachments/720x960_1e678b0f8c4e7ac16985e47beb4e96c1-jpg.108921/",
    ]

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

    def _leakedmodels_process_filename(self, url):
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
        results = []
        if is_leakedmodels_domain(html) or url == "test":
            results.extend([data[0] for data in set(re.findall(cls.VALID_URL_RE, html))])
        return results


class LeakedmodelsForumVideoExtractor(ExtractorBase, LeakedmodelsForumAuth):
    VALID_URL_RE = re.compile(PATTERN_LEAKEDMODELSFORUM_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "leakedmodels.com"
    DESC = "Leakedmodels Forum Video"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://cdn.leakedmodels.com/forum/data/video/108/108726-9031a9571acf19116bef07707a841655.mp4",
        "https://cdn.leakedmodels.com/forum/data/video/108/108729-7a47d7fc8047f1c9f862434c234a865c.mp4",
        "https://cdn.leakedmodels.com/forum/data/video/108/108730-92433769927ac80cbb7512430ce371a1.mp4",
        "https://cdn.leakedmodels.com/forum/data/video/108/108748-ecf11ec2fa878794f5d9d25c9f31d8fc.mp4",
        "https://cdn.leakedmodels.com/forum/data/video/108/108821-c6ae0aee8c2ceb45f0734a1bd32f8d09.m4v",
    ]

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
