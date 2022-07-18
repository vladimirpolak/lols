from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from utils import split_filename_ext
import re

PATTERN_ANONFILES = r"(?:https?://)anonfiles\.com/[\w\d]+/[\w\d-]+_[a-zA-Z\d]+"
PATTERN_ANONFILES_DLTAG = r'"download-url"(?s).*?href="(.*?)">'


class AnonfilesExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_ANONFILES)  # Regex pattern for url validation
    PROTOCOL = "https"  # http/s
    DOMAIN = "anonfiles.com"
    DESC = "AnonFiles File Storage"
    CONTENT_TYPE = "ITEM"  # ITEM/ALBUM/THREAD  None if unknown
    SAMPLE_URLS = [
        "https://anonfiles.com/V5gdWcy8y3/2gncGl6HwCzfH9Dg_mp4",  # Video
        "https://anonfiles.com/H3h4W5y3y3/200222787_195947142418120_7120636900489110320_n_jpg",  # Image
        "https://anonfiles.com/B3h0W9ydyb/z143_l_jpg",
        "https://anonfiles.com/J5heW6y8ya/l8jqf882kzp11_png",
        "https://anonfiles.com/F6h0W0y2yd/EubtFQLVEAEsLAj_jpg"
    ]

    def _extract_data(self, url):
        response = self._request_page(
            url=url,
        )
        html = response.text
        result = re.findall(PATTERN_ANONFILES_DLTAG, html)

        if result:
            if isinstance(result, str):
                source = result
            elif isinstance(result, list):
                source = result[0]
        else:
            raise ExtractionError(f"Failed to download URL from: {url}")

        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type_(extension)
        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )
