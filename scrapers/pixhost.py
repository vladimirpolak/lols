from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions
from exceptions import ExtractionError
from utils import split_filename_ext
import re

# Constant URLs
IMAGE_DIRECT_URL = "https://img{server_num}.pixhost.to/images{url_path}"

# Regex Patterns
PATTERN_PIXHOST_THUMBNAIL = rf"(https://t(\d+)\.pixhost\.to/thumbs(/\d+/[-\d\w]+(?:{'|'.join(img_extensions)})))"


class PixHostTHExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_PIXHOST_THUMBNAIL)
    PROTOCOL = "https"
    DOMAIN = "pixhost.to"
    DESC = "PixHost Image Hosting (Extract from thumbnail)"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://t37.pixhost.to/thumbs/355/131446931_daisy-keech_2___b6qtqyup0em.jpg"
    ]

    def _extract_data(self, url):
        try:
            data = self.VALID_URL_RE.findall(url)[0]
            server_num = data[1]
            url_path = data[2]
        except IndexError:
            raise ExtractionError(f"Failed to retrieve data from: {url}")

        source = IMAGE_DIRECT_URL.format(
            server_num=server_num,
            url_path=url_path
        )
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
    def extract_from_html(cls, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]
