from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type, img_extensions
from ..exceptions import ExtractionError
from ..utils import split_filename_ext

import re

_CODENAME = "ibam"

# Regex Patterns
PATTERN_IMAGEBAM_INDIRECT_LINK = r"((?:https?://)?(?:www\.)?imagebam\.com/(?:image|view)/[a-zA-Z\d]+)"
PATTERN_IMAGEBAM_DIRECT_LINK = rf"(https://images\d+\.imagebam\.com[-\w\d/]+(?:{'|'.join(img_extensions)}))"


class ImageBamExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMAGEBAM_INDIRECT_LINK)
    PROTOCOL = "https"
    DOMAIN = "imagebam.com"
    DESC = "ImageBam Image Hosting (Indirect Link)"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_direct_url(html, url)
        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )

    def _extract_direct_url(self, html, origin_url):
        result = set(re.findall(PATTERN_IMAGEBAM_DIRECT_LINK, html, re.I))
        if not result:
            raise ExtractionError(f"Failed to extract direct link from: {origin_url}")
        return result.pop()
