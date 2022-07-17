from ._scraper_base import ExtractorBase
from exceptions import ExtractionError
from downloader.types import vid_extensions, img_extensions
import re


PATTERN_CYBERDROP_ALBUM = r"((?:https?://)?cyberdrop\.(?:to|me)/a/\w+)"
PATTERN_CYBERDROP_IMAGE = rf"((?:https?://)?fs-\d+?\.cyberdrop\.(?:to|me)/(.+?)({'|'.join(img_extensions)}))"
PATTERN_CYBERDROP_VIDEO = rf"((?:https?://)?fs-\d+?\.cyberdrop\.(?:to|me)/(.+?)({'|'.join(vid_extensions)}))"


class CyberdropAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_CYBERDROP_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "cyberdrop.me"
    DESC = "Cyberdrop storage"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://cyberdrop.me/a/prrohXbK",
        "https://cyberdrop.me/a/1NS4e26j",
        "https://cyberdrop.me/a/zKSYgxvK",
        "https://cyberdrop.me/a/xfTkGU4B",
        "https://cyberdrop.me/a/zpxILGL3",
    ]

    def _extract_data(self, url):
        response = self._request_page(
            url=url,
        )
        html = response.text

        results_images = set(re.findall(PATTERN_CYBERDROP_IMAGE, html, re.I))
        results_videos = set(re.findall(PATTERN_CYBERDROP_VIDEO, html, re.I))
        album_title = self._extract_title(html, url)

        if not results_images and not results_videos:
            raise ExtractionError(f"\n{url}\nFailed to extract any data.")

        for image_match in results_images:
            source = image_match[0]
            filename = image_match[1]
            extension = image_match[2]

            self.add_item(
                content_type="image",
                filename=filename,
                extension=extension,
                source=source,
                album_title=album_title
            )

        for video_match in results_videos:
            source = video_match[0]
            filename = video_match[1]
            extension = video_match[2]

            self.add_item(
                content_type="video",
                filename=filename,
                extension=extension,
                source=source,
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
    DESC = "CyberDrop Image Link"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://fs-01.cyberdrop.cc/Ry2VcDEU-Ai4pQo-lMK3thIS.jpeg",
        "https://fs-05.cyberdrop.to/pmcYpiB-rivbeT-2KjuEbQ3.jpeg",
        "https://fs-01.cyberdrop.cc/PinuV6Fs-4PqSro-gWAQ3bM1.jpeg",
        "https://fs-01.cyberdrop.cc/mlCKbS2X-dgSNyR-taejUtVI.jpeg",
        "https://fs-01.cyberdrop.cc/HTyQfoJu-2dBS3P-3OBgIkSu.jpeg"
    ]

    def _extract_data(self, url):
        match = self.VALID_URL_RE.match(url)

        filename = match[1]
        extension = match[2]

        self.add_item(
            content_type="image",
            filename=filename,
            extension=extension,
            source=url,
        )
