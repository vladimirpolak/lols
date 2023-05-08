from .forum_socialmediagirls_auth import ForumSMGAuth
from ._scraper_base import ExtractorBase, CrawlerBase
from ..http.types import determine_content_type, img_extensions, vid_extensions
from ..exceptions import ExtractionError
from ..utils import slugify

import re


_CODENAME = "forum_smg"

PATTERN_SMGFORUM_THREAD = r"(?:https://)?forums\.socialmediagirls\.com/threads/(?P<album_id>[-%\w\.]+)/?"
PATTERN_SMGFORUM_THREADTITLE = '<meta property="og:title" content="(?:Request - )?(?P<thread_title>.*?)"\s+/>'
PATTERN_SMGFORUM_THREAD_NEXTPAGE = r'<a\s+' \
                                   r'href="(/threads/{album_id}/page-\d+)"\s+' \
                                   r'class="[-\w\d\s]*pageNav-jump--next">'
PATTERN_SMGFORUM_VIDEO = re.compile(
    r'(?P<url>(?:https://)?'
    r'(?:symedia\.sexy-youtubers|'
    r'smgmedia\.socialmediagirls)\.com/'
    r'forum/'
    r'[/\d]+'
    rf'(?P<filename>[-\w]+)(?P<extension>{"|".join(vid_extensions)}))/?'
)
PATTERN_SMGFORUM_IMAGE = re.compile(
    r'(?P<url>(?:https://)?'
    r'(?:smgmedia\.socialmediagirls|'
    r'symedia\.sexy-youtubers)\.com/'
    r'forum/'
    r'[/\d]+'
    rf'(?P<filename>[-\w]+)(?P<extension>{"|".join(img_extensions)}))/?'
)
PATTERN_SMGFORUM_IMAGE_2 = re.compile(
    r'(?P<url>(?:https://)?'
    r'forums\.socialmediagirls\.com/'
    r'attachments/'
    rf'(?P<filename>[-\w]+?)-(?P<extension>{"|".join([ext[1:] for ext in img_extensions])})\.\d+)/?'
)


class ForumSMGCrawler(ForumSMGAuth, CrawlerBase):
    VALID_URL_RE = re.compile(PATTERN_SMGFORUM_THREAD)
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum Thread"
    CODENAME = _CODENAME

    def initialize(self):
        self.authorize()

    def _crawl_link(self, url):
        self.album_id = self.VALID_URL_RE.search(url).group('album_id')

        while url:
            html, next_page = self._get_html_nextpage(url)
            yield url, html, next_page
            url = next_page

    def _get_html_nextpage(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        if self.username not in html:
            raise ExtractionError(f"Not authorized! (Most likely login session is expired.)")
        if not self.THREAD_NAME:
            self.THREAD_NAME = self.extract_threadname(html)
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
                return self.base_url + url_path
        return None

    def extract_threadname(self, html):
        match = re.search(PATTERN_SMGFORUM_THREADTITLE, html)
        if not match:
            return None
        title = match.group('thread_title')
        return self._parse_title(title)

    @staticmethod
    def _parse_title(title: str):
        if "/" in title:
            title = title.split("/")[-1].strip()
        return slugify(title, sep="_", del_special_chars=True)


class ForumSMGimageExtractor(ExtractorBase):
    VALID_URL_RE = [
        PATTERN_SMGFORUM_IMAGE,
        PATTERN_SMGFORUM_IMAGE_2
    ]
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum Image"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        filename, extension = self.parse_url(url)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )

    def parse_url(self, url) -> tuple:
        p = self._get_pattern(url)
        return self.extract_info(url, p)

    def _get_pattern(self, url) -> re.Pattern:
        for p in self.VALID_URL_RE:
            if p.match(url):
                return p
        raise ExtractionError()

    def extract_info(self, url: str, pattern: re.Pattern) -> tuple:
        results = pattern.search(url)
        filename = results.group('filename')
        extension = results.group('extension')
        if not extension.startswith("."):
            extension = "." + extension
        return filename, extension

    @classmethod
    def extract_from_html(cls, url, html):
        output = []
        for pattern in cls.VALID_URL_RE:
            output.extend([data[0] for data in set(pattern.findall(html))])
        return output


class ForumSMGvideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_SMGFORUM_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum Video"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        filename, extension = self.parse_url(url)
        content_type = determine_content_type(extension)

        self.add_item(
            source=url,
            filename=filename,
            extension=extension,
            content_type=content_type,
        )

    @classmethod
    def parse_url(cls, url: str) -> tuple:
        result = cls.VALID_URL_RE.search(url)
        return result.group('filename'), result.group('extension')

    @classmethod
    def extract_from_html(cls, url, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]
