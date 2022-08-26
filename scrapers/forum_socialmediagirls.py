from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from .forum_socialmediagirls_auth import ForumSMGAuth
from config import Manager as config
from utils import split_filename_ext, slugify
import logging
import re
import json

PATTERN_SMGFORUM_THREAD = r"(?:https://)?forums\.socialmediagirls\.com/threads/(?P<album_id>[-\w\.]+)/?"
PATTERN_SMGFORUM_THREADTITLE = r'<h1 class="p-title-value"(?:.*)</span>(?P<thread_name>[-/\w\s]+)</h1>'
PATTERN_SMGFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                   r'href="(/threads/{album_id}/page-\d+)"\s+' \
                                   r'class="[-\w\d\s]*pageNav-jump--next">'


class ForumSMGCrawler(ForumSMGAuth, CrawlerBase):
    VALID_URL_RE = re.compile(PATTERN_SMGFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = []

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url):
        self.album_id = self.VALID_URL_RE.search(url).group('album_id')

        output = dict()

        while url:
            html, next_page = self._get_html_nextpage(url)
            if next_page:
                print(f"Next page: {next_page}")
            else:
                print("Thread end.")
            output[url] = html
            url = next_page

        return output

    def _get_html_nextpage(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        if self.username not in html:
            raise ExtractionError(f"Not authorized! (Most likely login session is expired.)")
        if not self.THREAD_NAME:
            self.THREAD_NAME = self.extract_threadname(html)
            print(self.THREAD_NAME)
        next_page = self._extract_nextpage(html)

        return html, next_page

    def _extract_nextpage(self, html):
        np_pattern = PATTERN_SMGFORUM_THREAD_NEXTPAGE.format(album_id=self.album_id)
        result = set(re.findall(np_pattern, html))
        if result:
            url_path = result.pop()
            if url_path.startswith("http"):
                return url_path
            else:
                return self.base_url + url_path[1:]
        return None

    def extract_threadname(self, html):
        results = re.search(PATTERN_SMGFORUM_THREADTITLE, html)
        if not results:
            return None
        title = results.group('thread_name')
        return self._parse_title(title)

    @staticmethod
    def _parse_title(title: str):
        if "/" in title:
            title = title.split("/")[-1].strip()
        return slugify(title, sep="_", del_special_chars=True)
