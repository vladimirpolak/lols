from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type
from ..exceptions import ExtractionError
from ..utils import split_filename_ext

import re

_CODENAME = "imghaha"

# Regex Patterns
PATTERN_IMAGEHAHA_URL = r"(?:https://)?imagehaha\.com/\w+/[-\w]+\.\w+"
PATTERN_IMAGEHAHA_DIRECTURL = r"((?:https://)?(?:img|i)\d+\.imagehaha\.com/i/\d+/\w+\.\w+/[-\w.]+)"


class ImagehahaExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMAGEHAHA_URL)
    PROTOCOL = "https"
    DOMAIN = "imagehaha.com"
    DESC = "Imagehaha Image hosting"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_direct_url(html, url)
        filename, extension = split_filename_ext(source.split("/")[-1])
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )

    def _extract_direct_url(self, html, origin_url) -> str:
        result = re.findall(PATTERN_IMAGEHAHA_DIRECTURL, html, re.I)
        if not result:
            raise ExtractionError(f"Failed to extract direct url for image: {origin_url}")
        return result.pop()
