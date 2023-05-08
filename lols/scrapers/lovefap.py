from ..utils import split_filename_ext
from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type
from ..exceptions import ExtractionError, ScraperInitError, ContentTypeError, ParsingError

from typing import Set, List

import re
import logging

_CODENAME = "lovefap"

# Regex Patterns
PATTERN_LOVEFAP_ALBUM = r'(?:https:\/\/)?lovefap\.com\/a/[-\w]+'
PATTERN_LOVEFAP_VIDEOPAGE = r'(?:(?:https:\/\/)?lovefap\.com)?/video/[-\w]+'
PATTERN_LOVEFAP_IMAGE_DIRECT = r'(?:https:\/\/)?s\d*\.lovefap\.com\/content\/photos\/[-\w\.]+'
PATTERN_LOVEFAP_VIDEO_DIRECT = r'(?:https:\/\/)?s\d*\.lovefap\.com\/content\/videos\/[-\w\.]+'


class LoveFapAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_LOVEFAP_ALBUM)  # Regex pattern for url validation
    PROTOCOL = "https"
    DOMAIN = "lovefap.com"
    DESC = "LoveFap File Hosting"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        for url in self._extract_content(html):
            self._parse_url(url)

    def _extract_content(self, html) -> List[str]:
        image_urls = self._extract_images(html)
        video_urls = self._extract_videos(html)
        return image_urls + video_urls


    def _extract_images(self, html) -> List[str]:
        return list(set(re.findall(PATTERN_LOVEFAP_IMAGE_DIRECT, html)))

    def _extract_videos(self, html) -> List[str]:
        output = []
        indirect_urls: Set[str] = set(re.findall(PATTERN_LOVEFAP_VIDEOPAGE, html))
        for url in indirect_urls:
            if not url.startswith("http"):
                url = self.base_url + url
            res = self.request(url=url)
            if res.ok:
                result = re.search(PATTERN_LOVEFAP_VIDEO_DIRECT, res.text)
                if result:
                    output.append(result.group(0))
                else:
                    logging.error(f"Error accessing url: '{url}', Response Code: {res.status_code}")
        return output

    def _parse_url(self, url: str):
        try:
            source = url
            filename, extension = split_filename_ext(url.split("/")[-1])
            content_type = determine_content_type(extension)
        except ContentTypeError as e:
            logging.error(f"Error parsing url '{url}' {e}")
        else:
            self.add_item(
                source=source,
                filename=filename,
                extension=extension,
                content_type=content_type,
            )