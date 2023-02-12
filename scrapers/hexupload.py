from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type
from exceptions import ExtractionError
from utils import split_filename_ext
import re

# Constant URLs

# Regex Patterns
PATTERN_HEXUPLOAD = r"https://hexupload.net/[a-z\d]+"
VIDEO_ELEMENT = r'<source\s+' \
                r'src="(https://\d+\.contenthx\.me/d/\w+/video\.mp4)"' \
                r'\s+type="video/mp4">'


class HexuploadVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_HEXUPLOAD)
    PROTOCOL = "https"
    DOMAIN = "hexupload.net"
    DESC = "Hexupload Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://hexupload.net/761mnw2p5y9c",
        "https://hexupload.net/77k0me3rh1vx",
        "https://hexupload.net/4xrnvo5tp8tx",
        "https://hexupload.net/gsollprm9rh2",
        "https://hexupload.net/5lr9ql7ko7vp"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_direct_link(html)
        file_w_ext = self._extract_filename(html)

        self._validate(source, file_w_ext, url)

        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _validate(self, source, filename, url):
        if not source and not filename:
            raise ExtractionError(f"Failed to extract source and filename: {url}")
        elif not source:
            raise ExtractionError(f"Failed to extract source: {url}")
        elif not filename:
            raise ExtractionError(f"Failed to extract filename: {url}")

    def _extract_filename(self, html):
        pattern = re.compile(
            r'<h2\s+style="word-break:\s+break-all;">(.*)</h2>'
        )
        result = pattern.findall(html)
        try:
            return result[0]
        except IndexError:
            return None

    def _extract_direct_link(self, html):
        pattern = re.compile(VIDEO_ELEMENT)
        result = pattern.findall(html)
        try:
            return result[0]
        except IndexError:
            return None

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
