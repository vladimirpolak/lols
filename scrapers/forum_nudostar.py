from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type, vid_extensions
from utils import split_filename_ext, slugify
from exceptions import ExtractionError
from .forum_nudostar_auth import ForumNudostarAuth
from typing import Union
import re

# Regex Patterns
PATTERN_NUDOSTARFORUM_THREAD = r"(?:https://)?nudostar\.com/forum/threads/([-\w\.]+)/?"
PATTERN_NUDOSTARFORUM_CONTENT = re.compile(
    r"((?:(?:https://)?nudostar\.com)?/forum/attachments/([-\w]+)-([a-zA-Z\d]+)\.\d+/?)"
)
# ---------------------- Depreicated
# PATTERN_NUDOSTARFORUM_VIDEO = re.compile(
#     rf"((?:(?:https://)?nudostar\.com)?/forum/data/video/\d+/[-\w]+(?:{'|'.join(vid_extensions)}))"
# )
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

        output = dict()

        while url:
            html, next_page = self._get_html_nextpage(url)
            output[url] = html

            if next_page:
                # Break if custom page limit has been reached
                if self.page_limit and len(output) == self.page_limit:
                    break
                print(f"Next page: {next_page}")
            else:
                print("Thread end.")
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

class ForumNudostarContentExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_CONTENT)
    PROTOCOL = "https"
    DOMAIN = "nudostar.com"
    DESC = "Nudostar Forum Content"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://nudostar.com/forum/attachments/rn1yfyd2og471-jpg.895744/",
        "https://nudostar.com/forum/attachments/f6b2f53d-93ce-46e0-a4af-051f52552b92-jpeg.895754/",
        "https://nudostar.com/forum/attachments/adore_sophia-story-18-03-2022-mp4.3283022/"
    ]

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
    def extract_from_html(cls, html):
        results = []
        if is_nudostar_domain(html):
            results.extend([data[0] for data in set(re.findall(cls.VALID_URL_RE, html))])
        return results

# --------------------- Depricated
# class ForumNudostarVideoExtractor(ExtractorBase):
#     VALID_URL_RE = re.compile(PATTERN_NUDOSTARFORUM_VIDEO)
#     PROTOCOL = "https"
#     DOMAIN = "nudostar.com"
#     DESC = "Nudostar Forum Video"
#     CONTENT_TYPE = "ITEM"
#     SAMPLE_URLS = [
#         "https://nudostar.com/forum/data/video/1639/1639695-aa0598d17264f7e9002f653e9e446295.mp4",
#         "https://nudostar.com/forum/data/video/1639/1639696-dce64cca4e52895283c02d1b317e904f.mp4",
#         "/forum/data/video/1639/1639697-b49a90ba4f5727d1cddc36e736094ceb.mp4"
#     ]
#
#     def _extract_data(self, url):
#         if url.startswith("https"):
#             source = url
#         else:
#             source = self.base_url + url
#         file_w_extension = source.split("/")[-1]
#         filename, extension = split_filename_ext(file_w_extension)
#         content_type = determine_content_type(extension)
#
#         self.add_item(
#             content_type=content_type,
#             filename=filename,
#             extension=extension,
#             source=source
#         )
#
#     @classmethod
#     def extract_from_html(cls, url, html):
#         results = []
#         if is_nudostar_domain(html) or url == "test":
#             results.extend([data for data in set(re.findall(cls.VALID_URL_RE, html))])
#         return results

