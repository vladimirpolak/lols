from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from utils import split_filename_ext
import re

# Regex Patterns
PATTERN_IMAGEHAHA_URL = r"(?:https://)?imagehaha\.com/[\w\d]+/[-\d\w]+\.[\w\d]+"
PATTERN_IMAGEHAHA_DIRECTURL = r"((?:https://)?(?:img|i)\d+\.imagehaha\.com/i/\d+/[\w\d]+\.[\d\w]+/[-\d\w.]+)"


class ImagehahaExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMAGEHAHA_URL)
    PROTOCOL = "https"
    DOMAIN = "imagehaha.com"
    DESC = "Imagehaha Image hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://imagehaha.com/p93zfz84jzij/3840x5761_21d8a2b87effccb7a2f0efff33fb8392.jpg",
        "https://imagehaha.com/07ruwzb5lhqd/3840x5761_dbbc4f9f708b063cc02f572dac60ffff.jpg",
        "https://imagehaha.com/lwn5mctpo201/3840x5241_05c475beb86842696d0cf60069dc7edf.jpg",
        "https://imagehaha.com/bguyye73fah1/3840x2560_255dbcc9d07cba639a9e1c4e615c61eb.jpg"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_direct_url(html, url)
        filename, extension = split_filename_ext(source.split("/")[-1])
        content_type = determine_content_type_(extension)

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

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
