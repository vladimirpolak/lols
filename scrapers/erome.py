from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from utils import split_filename_ext
import re

PATTERN_EROME_ALBUM = r"(?:https://)?(?:www\.)?erome\.com/a/\w+"
PATTERN_EROME_IMAGE = rf"(?:https://)?s\d+\.erome\.com/\d+/\w+/\w+(?:{'|'.join(img_extensions)})\?v=\d+"
PATTERN_EROME_VIDEO = rf"(?:https://)?s\d+\.erome\.com/\d+/\w+/\w+(?:{'|'.join(vid_extensions)})"


class EromeAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_EROME_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "erome.com"
    DESC = "Erome Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://www.erome.com/a/69MH41fn",
        "https://www.erome.com/a/srArB7Yt"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        urls = []
        urls.extend(self.extract_image_urls(html))
        urls.extend(self.extract_video_urls(html))

        for url in urls:
            filename, extension, content_type = self.parse_url(url)
            headers = {
                'referer': 'https://www.erome.com/'
            }

            self.add_item(
                source=url,
                filename=filename,
                extension=extension,
                content_type=content_type,
                headers=headers
            )

    def extract_image_urls(self, html: str, pattern: str = PATTERN_EROME_IMAGE) -> list:
        return self._extract(pattern, html)

    def extract_video_urls(self, html: str, pattern: str = PATTERN_EROME_VIDEO) -> list:
        return self._extract(pattern, html)

    @staticmethod
    def _extract(pattern, html):
        return list(set(re.findall(pattern, html)))

    def parse_url(self, url: str):
        filename_w_extension = self._extract_filename(url)
        filename, extension = split_filename_ext(filename_w_extension)
        content_type = determine_content_type_(extension)
        return filename, extension, content_type

    @staticmethod
    def _extract_filename(url: str) -> str:
        if re.match(PATTERN_EROME_IMAGE, url):
            return url.split("?v")[0].split("/")[-1]
        return url.split("/")[-1]

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
