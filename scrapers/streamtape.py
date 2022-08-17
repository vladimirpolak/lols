from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, vid_extensions
from exceptions import ExtractionError
from utils import split_filename_ext, slugify
import re

ID = str
Expires = int
IP = str
Token = str

URL_STREAMTAPE_GETVIDEO = "https://streamtape.com/get_video"

PATTERN_STREAMTAPE_VIDEO = rf'(?:https://)?streamtape\.com/v/[a-zA-Z\d]+/[-\w\d]+(?:{"|".join(vid_extensions)})'
PATTERN_STREAMTAPE_GETVIDEO_PARAMS = re.compile(
    r"\('[a-z]+\?"
    r"id=(?P<id>[a-zA-Z\d]+)"
    r"&expires=(?P<expires>\d+)"
    r"&ip=(?P<ip>[a-zA-Z\d]+)"
    r"&token=(?P<token>[-a-zA-Z\d]+)"
    r"'\)"
)


def getvideo_headers(url: str):
    return {
        'accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
        'accept-encoding': 'identity;q=1, *;q=0',
        'range': 'bytes=0-',
        'referer': url,
        'sec-fetch-dest': 'video',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'connection': 'keep-alive',
        'host': 'streamtape.com'
    }


def getvideo_params(id_param: str, expires: int, ip: str, token: str):
    return {
        'id': id_param,
        'expires': expires,
        'ip': ip,
        'token': token,
        'stream': 1
    }


class StreamtapeVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_STREAMTAPE_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "streamtape.com"
    DESC = "Streamtape Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://streamtape.com/v/L280lgyDKWfa82/Lauren_Alexis_Fuck_Me_Daddy_Video_Leaked.mp4"
    ]

    def _extract_data(self, url):
        self.origin_url = url

        response = self.request(
            url=self.origin_url,
        )
        html = response.text

        source = self._extract_directurl(html)
        file_w_ext = self._extract_title(html)
        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _extract_directurl(self, html):
        # Extract url parameters for direct url from html
        id_param, expires, ip, token = self._extract_getvideo_params(html)

        params = getvideo_params(id_param, expires, ip, token)
        headers = getvideo_headers(self.origin_url)

        response = self.request(
            url=URL_STREAMTAPE_GETVIDEO,
            params=params,
            headers=headers,
            allow_redirects=False
        )
        res_headers = response.headers
        return res_headers["Location"]

    def _extract_getvideo_params(self, html) -> (ID, Expires, IP, Token):
        """Extracts parameters for get_video url."""
        params = PATTERN_STREAMTAPE_GETVIDEO_PARAMS.search(html)
        if params:
            return params.group('id'), params.group('expires'), params.group('ip'), params.group('token')
        else:
            raise ExtractionError(
                f"Failed to extract 'get_video' params from html: {self.origin_url}"
            )

    def _extract_title(self, html):
        """Extracts title of the video."""
        p = re.compile(
            r'"showtitle":"(.*?)"'
        )
        result = p.search(html)
        if result:
            title = result.group(1)
            return slugify(title)
        else:
            raise ExtractionError(
                f"Failed to extract title from html: {self.origin_url}"
            )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
