from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions
from exceptions import ExtractionError
from utils import split_filename_ext
import re

# Regex Patterns
PATTERN_IMAGEBAM_INDIRECT_LINK = r"((?:https?://)?(?:www\.)?imagebam\.com/image/[a-z\d]+)"
PATTERN_IMAGEBAM_DIRECT_LINK = rf"(https://images\d+\.imagebam\.com[a-z\d/]+(?:{'|'.join(img_extensions)}))"


class ImageBamExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMAGEBAM_INDIRECT_LINK)
    PROTOCOL = "https"
    DOMAIN = "imagebam.com"
    DESC = "ImageBam Image Hosting (Indirect Link)"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://www.imagebam.com/image/c444481329385981",
        "https://www.imagebam.com/image/9f75e71329338706",
        "https://www.imagebam.com/image/8211d41329585369",
        "https://www.imagebam.com/image/39e9741330023251",
        "https://www.imagebam.com/image/96fb7d1330023260"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        result = set(re.findall(PATTERN_IMAGEBAM_DIRECT_LINK, html, re.I))
        if not result:
            raise ExtractionError(f"Failed to extract direct link from: {url}")

        source = result.pop()
        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )

    @classmethod
    def _extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
