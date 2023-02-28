from ._scraper_base import ExtractorBase
from exceptions import ExtractionError
from downloader.types import vid_extensions, img_extensions, determine_content_type
import re

_CODENAME = "cdrop"

# Regex Patterns
PATTERN_CYBERDROP_ALBUM = r"((?:https?://)?cyberdrop\.(?:to|me|cc)/a/\w+)"
PATTERN_CYBERDROP_IMAGE = rf"((?:https?://)?fs-\d+?\.cyberdrop\.(?:to|me|cc)/(.+?)({'|'.join(img_extensions)}))"
PATTERN_CYBERDROP_VIDEO = rf"((?:https?://)?fs-\d+?\.cyberdrop\.(?:to|me|cc)/(.+?)({'|'.join(vid_extensions)}))"


class CyberdropAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_CYBERDROP_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "cyberdrop.me"
    DESC = "Cyberdrop Album"
    CONTENT_TYPE = "ALBUM"
    CODENAME = _CODENAME
    SAMPLE_URLS = [
        "https://cyberdrop.me/a/prrohXbK",
        "https://cyberdrop.me/a/1NS4e26j",
        "https://cyberdrop.me/a/zKSYgxvK",
        "https://cyberdrop.me/a/xfTkGU4B",
        "https://cyberdrop.me/a/zpxILGL3",
    ]

    @classmethod
    def is_active(cls):
        return False

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        results_images = list(set(re.findall(PATTERN_CYBERDROP_IMAGE, html, re.I)))
        results_videos = list(set(re.findall(PATTERN_CYBERDROP_VIDEO, html, re.I)))
        album_title = self._extract_title(html, url)

        if not results_images and not results_videos:
            raise ExtractionError(f"\n{url}\nFailed to extract any data.")

        results = results_images + results_videos
        for item in results:
            source = item[0]
            filename = item[1]
            extension = item[2]
            content_type = determine_content_type(extension)

            self.add_item(
                source=source,
                filename=filename,
                extension=extension,
                content_type=content_type,
                album_title=album_title
            )

    def _extract_title(self, html, url):
        title_pattern = re.compile(
            r'<h1 id="title" .*>\s*(.*)\s*</h1>'
        )
        match = re.findall(title_pattern, html)
        if not match:
            raise ExtractionError(f"{url}\nFailed to extract album title.")
        return match[0]


class CyberdropImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_CYBERDROP_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "cyberdrop.com"
    DESC = "CyberDrop Image URL"
    CONTENT_TYPE = "ITEM"
    CODENAME = _CODENAME
    SAMPLE_URLS = [
        "https://fs-01.cyberdrop.cc/Ry2VcDEU-Ai4pQo-lMK3thIS.jpeg",
        "https://fs-05.cyberdrop.to/pmcYpiB-rivbeT-2KjuEbQ3.jpeg",
        "https://fs-01.cyberdrop.cc/PinuV6Fs-4PqSro-gWAQ3bM1.jpeg",
        "https://fs-01.cyberdrop.cc/mlCKbS2X-dgSNyR-taejUtVI.jpeg",
        "https://fs-01.cyberdrop.cc/HTyQfoJu-2dBS3P-3OBgIkSu.jpeg"
    ]

    @classmethod
    def is_active(cls):
        return False

    def _extract_data(self, url):
        match = self.VALID_URL_RE.match(url)

        filename = match[1]
        extension = match[2]
        content_type = determine_content_type(extension)

        self.add_item(
            source=url,
            content_type=content_type,
            filename=filename,
            extension=extension,
        )

    @classmethod
    def extract_from_html(cls, url, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]

