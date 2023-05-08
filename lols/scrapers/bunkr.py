from ._scraper_base import ExtractorBase
from ..http.types import (determine_content_type,
                          vid_extensions,
                          ContentType)
from ..exceptions import ExtractionError, ContentTypeError
from ..utils import split_filename_ext

from w3lib.html import replace_entities
from typing import List, Union
import logging
import re

_CODENAME = "bunkr"

# Regex Patterns
PATTERN_BUNKR_ALBUM = r"(?:https?://)?bunkr\.[a-z]+/a/\w+"
PATTERN_BUNKR_ALBUM_CONTENT = rf"(?:https?://)?cdn\d*.bunkr\.[a-z]+/[-,&;?!%.\w\(\)\[\]]+"
PATTERN_BUNKR_VIDEO_URL = rf"(?:https?://)(?:stream|media-files|cdn)\d*\.bunkr\.[a-z]+/(?:v/)?[-~%\w]+(?:{'|'.join(vid_extensions)})"
# TODO https://cdn9.bunkr.ru/3840x2880_e1a8da6df3f70e9925d046545d9eb7f5-OjsUr42k.jpg


def extract_download_url_from_videopage(videopage_html: str) -> str:
    pattern = re.compile(r'https://media-files\d*\.bunkr\.[a-z]+/[-,&;?!%.\w]+')
    result = re.search(pattern, videopage_html)
    if result:
        return result.group(0)
    return ""


class BunkrAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr Album"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        self.url = url
        response = self.request(
            url=self.url,
            headers={
                "accept": "application/signed-exchange;v=b3;q=0.9"
            }
        )
        html = response.text
        extracted_urls = self._extract_content(html)
        self._parse_urls(extracted_urls)

    def _extract_content(self, html) -> List[str]:
        return re.findall(PATTERN_BUNKR_ALBUM_CONTENT, html)

    def _parse_urls(self, urls: List[str]):
        for url in urls:
            filename_w_ext = url.split("/")[-1]
            filename, extension = split_filename_ext(filename_w_ext)

            try:
                content_type = determine_content_type(extension)
            except ContentTypeError:
                logging.error(
                    f"PARSING ERROR:: "
                    f"OriginUrl: '{self.url}' "
                    f"Url: '{url}' "
                    f"Filename: '{filename}' "
                    f"Extension: '{extension}'"
                )
            else:
                if content_type == ContentType.VIDEO:
                    source = extract_download_url_from_videopage(
                        self.request(replace_entities(url)).text
                    )
                else:
                    source = url

                if not source:
                    logging.error(f"Failed to parse download url for: {url}")
                else:
                    self.add_item(
                        source=source,
                        filename=replace_entities(filename),
                        extension=extension,
                        content_type=content_type
                    )


class BunkrVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_VIDEO_URL)
    PROTOCOL = "https"
    DOMAIN = "stream.bunkr.is"
    DESC = "Bunkr Video Page"
    CODENAME = _CODENAME
    SAMPLE_URLS = [
        "https://stream.bunkr.is/v/ea_vid_14-9a9Jq32V.mov",
        "https://stream.bunkr.is/v/ea_vid_12-rlwMZzT1.mov",
        "https://stream.bunkr.is/v/lai_vid_3-3Ymk80tH.mp4",
        "https://cdn.bunkr.is/0h1owpgtrqdncpvflf8ey_source-XltlzTqe.mp4",
        "https://cdn3.bunkr.is/IMG_1141-6RvpacEH.MOV"
    ]

    def _extract_data(self, url: str):
        filename_w_ext = url.split("/")[-1]
        filename, extension = split_filename_ext(filename_w_ext)
        content_type = determine_content_type(extension)
        source = extract_download_url_from_videopage(
            self.request(url).text
        )

        if not source:
            raise ExtractionError(f"Failed to parse download url for: {url}")
        else:
            self.add_item(
                source=source,
                filename=filename,
                extension=extension,
                content_type=content_type
            )
