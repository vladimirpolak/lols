from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions
from exceptions import ExtractionError
from utils import split_filename_ext
import re

# Regex Patterns
PATTERN_IMAGETWIST_INDIRECT_LINK = r"((?:https://)?imagetwist\.com/" \
                     rf"[a-z\d]+/[-\w\d]+(?:{'|'.join(img_extensions)}))"
PATTERN_IMAGETWIST_DIRECT_LINK = r"(?:https://)?(?:i|img)\d+\.imagetwist\.com/i/" \
                                 r"\d+/" \
                                 rf"[-\w\d]+(?:{'|'.join(img_extensions)})/" \
                                 rf"[-\w\d]+(?:{'|'.join(img_extensions)})"


class ImageTwistImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMAGETWIST_INDIRECT_LINK)
    PROTOCOL = "https"
    DOMAIN = "imagetwist.com"
    DESC = "ImageTwist Image Hosting (Indirect Link)"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://imagetwist.com/4oq69uqte9w5/3031x2583_23c06901eafb23628008996b51db8cc3.jpg",
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_direct_link(html)
        if not source:
            raise ExtractionError(f"Failed to extract direct link for image: {url}")

        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _extract_direct_link(self, html):
        results = set(re.findall(PATTERN_IMAGETWIST_DIRECT_LINK, html, re.I))
        if results:
            return results.pop()
        return None

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
