from downloader.types import (determine_content_type,
                              vid_extensions,
                              ContentType)
from ._scraper_base import ExtractorBase
from exceptions import ExtractionError
from utils import split_filename_ext
from typing import List
import logging
import re

# Regex Patterns
PATTERN_BUNKR_ALBUM = r"(?:https?://)?bunkr\.[a-z]+/a/\w+"
PATTERN_BUNKR_ALBUM_CONTENT = rf"(?:https?://)?cdn\d*.bunkr\.[a-z]+/[-.\w]+"
PATTERN_BUNKR_VIDEO_URL = rf"(?:https?://)(?:stream|media-files|cdn)\d*\.bunkr\.[a-z]+/(?:v/)?[-~%\w]+(?:{'|'.join(vid_extensions)})"


def video_download_url(video_url: str) -> str:
    pattern = re.compile(
        r"(?:https?://)?(?:cdn|stream)(?P<server_num_domain>\d*\.bunkr\.[a-z]+)/(?:v/)?(?P<filename>[-.\w]+)"
    )
    parse = re.match(pattern, video_url)
    logging.debug(f"Parsing...{video_url}...Result: {parse.groupdict()}")
    if not parse:
        return ""
    return f"https://media-files{parse.group('server_num_domain')}/{parse.group('filename')}"


class BunkrAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr.is Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://bunkr.is/a/rXQtFw5W",
        "https://bunkr.is/a/jBCopZia",
        "https://bunkr.is/a/G6Mzbwpv",
        "https://bunkr.is/a/TCxaRKiw",
        "https://bunkr.is/a/XCIfbTX8"
    ]

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
        self._parse_items(extracted_urls)

    def _extract_content(self, html) -> List[str]:
        return re.findall(PATTERN_BUNKR_ALBUM_CONTENT, html)

    def _parse_items(self, urls: List[str]):
        for url in urls:
            filename_w_ext = url.split("/")[-1]
            filename, extension = split_filename_ext(filename_w_ext)
            content_type = determine_content_type(extension)

            if content_type == ContentType.VIDEO:
                source = video_download_url(url)
            else:
                source = url

            if not source:
                logging.error(f"Failed to parse download url for: {url}")
            else:
                self.add_item(
                    source=source,
                    filename=filename,
                    extension=extension,
                    content_type=content_type
                )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]


class BunkrVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_VIDEO_URL)
    PROTOCOL = "https"
    DOMAIN = "stream.bunkr.is"
    DESC = "Bunkr.is Video Page"
    CONTENT_TYPE = "ITEM"
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
        source = video_download_url(url)

        if not source:
            raise ExtractionError(f"Failed to parse download url for: {url}")
        else:
            self.add_item(
                source=source,
                filename=filename,
                extension=extension,
                content_type=content_type
            )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
