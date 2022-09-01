from ._scraper_base import ExtractorBase
from ..downloader.types import determine_content_type_
from ..utils import split_filename_ext
from ..exceptions import ExtractionError
import re

# Regex Patterns
PATTERN_ANONFILES = r"(?:https?://)?anonfiles\.com/[-/\w]+"
PATTERN_ANONFILES_DLTAG = r'"download-url"(?s).*?href="(.*?)">'


class AnonfilesExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_ANONFILES)
    PROTOCOL = "https"
    DOMAIN = "anonfiles.com"
    DESC = "AnonFiles File Storage"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://anonfiles.com/r7ldQ8r2wd/2021-12-17-15-34-25_NCARHYdP-1_mp4",
        "https://anonfiles.com/H3h4W5y3y3/200222787_195947142418120_7120636900489110320_n_jpg",
        "https://anonfiles.com/B3h0W9ydyb/z143_l_jpg",
        "https://anonfiles.com/J5heW6y8ya/l8jqf882kzp11_png",
        "https://anonfiles.com/F6h0W0y2yd/EubtFQLVEAEsLAj_jpg"
    ]

    def _extract_data(self, url):
        # Get the page
        response = self.request(
            url=url,
        )
        html = response.text

        source = self._extract_download_url(html, url)

        # Parse the data
        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type_(extension)

        # Add item to output
        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )

    def _extract_download_url(self, html: str, origin_url: str):
        result = re.findall(PATTERN_ANONFILES_DLTAG, html)
        if not result:
            raise ExtractionError(f"Failed to extract download url from: {origin_url}")
        return result.pop()


    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]