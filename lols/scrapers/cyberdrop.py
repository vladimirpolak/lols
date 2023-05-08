from ..http.types import vid_extensions, img_extensions, determine_content_type
from ..exceptions import ExtractionError
from ._scraper_base import ExtractorBase

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
    CODENAME = _CODENAME

    # @classmethod
    # def is_active(cls):
    #     return False

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
    CODENAME = _CODENAME

    # @classmethod
    # def is_active(cls):
    #     return False

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

