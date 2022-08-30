from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError
from .forum_socialmediagirls_auth import ForumSMGAuth
from utils import slugify
import re


PATTERN_SMGFORUM_THREAD = r"(?:https://)?forums\.socialmediagirls\.com/threads/(?P<album_id>[-\w\.]+)/?"
PATTERN_SMGFORUM_THREADTITLE = r'<h1 class="p-title-value"(?:.*)</span>(?P<thread_name>[-/\w\s]+)</h1>'
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
    DESC = "SocialMediaGirls Forum"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://forums.socialmediagirls.com/threads/zlatasharv_-zlata-sharvarok-zlata_sh.27771/",
        "https://forums.socialmediagirls.com/threads/racharmstrong.209293/"
    ]

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


class ForumSMGimageExtractor(ExtractorBase):
    VALID_URL_RE = [
        PATTERN_SMGFORUM_IMAGE,
        PATTERN_SMGFORUM_IMAGE_2
    ]
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum Image"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://forums.socialmediagirls.com/attachments/photo_2019-08-25_21-30-20-jpg.375004/",
        "https://forums.socialmediagirls.com/attachments/960x1280_0a5e57b8e3616cae6108a08f7a7a1052-jpg.2454459/",
        "https://symedia.sexy-youtubers.com/forum/2020/06/photo_2019-09-28_23-38-58_391486.jpg",
        "https://symedia.sexy-youtubers.com/forum/2020/06/photo_2019-09-25_01-00-02_391484.jpg",
        "https://smgmedia.socialmediagirls.com/forum/2020/06/photo_2019-08-25_21-30-20_391478.jpg",
        "https://smgmedia.socialmediagirls.com/forum/2021/08/960x1280_0a5e57b8e3616cae6108a08f7a7a1052_2486310.jpg",
    ]

    def _extract_data(self, url):
        filename, extension = self.parse_url(url)
        content_type = determine_content_type_(extension)

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
    def extract_from_html(cls, html):
        output = []
        for pattern in cls.VALID_URL_RE:
            output.extend([data[0] for data in set(pattern.findall(html))])
        return output


class ForumSMGvideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_SMGFORUM_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "forums.socialmediagirls.com"
    DESC = "SocialMediaGirls Forum Video"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://symedia.sexy-youtubers.com/forum/2020/06/IMG_0508_391443.mp4",
        "https://symedia.sexy-youtubers.com/forum/2020/06/IMG_0058_391444.mp4",
        "https://smgmedia.socialmediagirls.com/forum/2020/06/IMG_0508_391443.mp4",
        "https://smgmedia.socialmediagirls.com/forum/2020/06/IMG_0058_391444.mp4",
    ]

    def _extract_data(self, url):
        filename, extension = self.parse_url(url)
        content_type = determine_content_type_(extension)

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
    def extract_from_html(cls, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]
