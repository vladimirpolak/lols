from ._scraper_base import ExtractorBase
from downloader.types import (determine_content_type_,
                            img_extensions,
                            vid_extensions,
                            archive_extensions,
                            ContentType)
from exceptions import ExtractionError
from utils import split_filename_ext
from typing import Union
import yarl
import logging
import re
import json

# Constant URLs
STREAM_URL = "https://media-files{server_num}.bunkr.is"

# Regex Patterns
PATTERN_BUNKR_ALBUM = r"((?:https?://)?bunkr\.is/a/\w+)"
PATTERN_BUNKR_ALBUM_DATA_SCRIPT = r'<script id="__NEXT_DATA__" type="application/json">(\{.*?})</script>'
PATTERN_BUNKR_VIDEO = rf"((?:https?://)(?:stream|media-files(\d)*|cdn(\d)*)\.bunkr\.is/(?:v/)?[-\w]+?(?:{'|'.join(vid_extensions)}))"
PATTERN_BUNKR_IMAGE = rf"((?:https://)?cdn\d+\.bunkr\.is/[-\w]+(?:{'|'.join(img_extensions)}))"
PATTERN_BUNKR_ARCHIVE = rf"((?:https://)?cdn\d+\.bunkr\.is/[-\w]+(?:{'|'.join(archive_extensions)}))"


def extract_server_number(url: str) -> int:
    pattern = re.compile(r"(?:cdn|stream|i|media-files)(\d)*\.bunkr\.is")
    return pattern.findall(url)[0]


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
                "Host": "bunkr.is"
            }
        )
        html = response.text

        # Extract the script that fetches album data in json format
        pattern = re.compile(PATTERN_BUNKR_ALBUM_DATA_SCRIPT)
        data_tag = re.search(pattern, html)

        if not data_tag:
            logging.debug(
                f"ERROR Didn't find data tag on page {self.url}."
            )

        # Load into json
        json_ = json.loads(data_tag.group(1))
        is_fallback = json_["isFallback"]

        if json_ and not is_fallback:
            page_props = json_["props"]["pageProps"]
        else:
            page_props = self._fallback_method(json_)

        try:
            title = page_props['album']['name']
            files = page_props['files']
        except KeyError as e:
            raise ExtractionError(
                f"Failed extracting '{e}'\n"
                f"Data: {page_props}"
            )

        logging.info(
            f"[SCRAPED] ALBUM TITLE: {title} "
            f"DATA LENGTH: {len(files)}"
        )

        for item in files:
            album_title = title
            file_w_extension = item['name']
            filename, extension = split_filename_ext(file_w_extension)
            content_type = determine_content_type_(extension)

            if content_type == ContentType.IMAGE:
                source = f"{item['i']}/{file_w_extension}"
            elif content_type == ContentType.VIDEO:
                server_num = extract_server_number(item['cdn'])
                source = f"{STREAM_URL.format(server_num=server_num)}/{file_w_extension}"
            elif content_type == ContentType.AUDIO:
                source = f"{item['cdn']}/{file_w_extension}"
            elif content_type == ContentType.ARCHIVE:
                source = f"{item['cdn']}/{file_w_extension}"
            else:
                raise NotImplementedError(
                    f"Error parsing data for bunkr.\n"
                    f"Data to parse: {item}"
                )

            self.add_item(
                content_type=content_type,
                filename=filename,
                extension=extension,
                source=source,
                album_title=album_title
            )

    def _fallback_method(self, json):
        url = yarl.URL(self.url)
        fetch_url = "https://" + url.host + "/_next/data/" + json['buildId'] + url.path + '.json'
        response = self.request(fetch_url)
        if response.status_code != 200:
            logging.debug(f"ERROR Failed to extract page data from {self.url}.")
        json_ = response.json()
        return json_["pageProps"]

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]


class BunkrVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "stream.bunkr.is"
    DESC = "Bunkr.is Video Page"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://stream.bunkr.is/v/ea_vid_14-9a9Jq32V.mov",
        "https://stream.bunkr.is/v/ea_vid_12-rlwMZzT1.mov",
        "https://stream.bunkr.is/v/lai_vid_3-3Ymk80tH.mp4",
        "https://stream.bunkr.is/v/rr_vid_12-3HiQTJtY.mp4",
        "https://cdn.bunkr.is/0h1owpgtrqdncpvflf8ey_source-XltlzTqe.mp4",
        "https://cdn3.bunkr.is/IMG_1141-6RvpacEH.MOV"
    ]

    def _extract_data(self, url: str):
        self.url = url
        if "stream.bunkr.is" in self.url:
            response = self.request(self.url)
            html = response.text
            if "<title>404: This page could not be found</title>" in html:
                return
            source = self._extract_direct_link(html)

            filename, extension = split_filename_ext(source.split("/")[-1])
            content_type = determine_content_type_(extension)

        else:
            server_num = extract_server_number(self.url)

            file_w_extension = self.url.split("/")[-1]
            filename, extension = split_filename_ext(file_w_extension)

            content_type = determine_content_type_(extension)

            source = f"{STREAM_URL.format(server_num=server_num)}/{file_w_extension}"

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _extract_direct_link(self, html) -> Union[str, None]:
        # Extract the script that fetches album data in json format
        pattern = re.compile(PATTERN_BUNKR_ALBUM_DATA_SCRIPT)
        data_tag = re.search(pattern, html)

        if not data_tag:
            logging.debug(
                f"Failed to extract data.\n"
                f"Didn't find html script tag containing data."
            )
            return None

        # Load into json
        json_ = json.loads(data_tag.group(1))
        is_fallback = json_["isFallback"]
        page_props = json_["props"]["pageProps"]

        if json_ and is_fallback:
            page_props = self._fallback_method(json_)

        item_info = page_props["file"]
        filename = item_info["name"]
        url_base = item_info["mediafiles"]
        return f"{url_base}/{filename}"

    def _fallback_method(self, json: dict):
        url = yarl.URL(self.url)
        fetch_url = "https://" + url.host + "/_next/data/" + json['buildId'] + url.path + '.json'
        response = self.request(fetch_url)
        if response.status_code != 200:
            logging.debug(f"ERROR Failed to extract data from {self.url}.")
        json_ = response.json()
        return json_["pageProps"]

    @classmethod
    def extract_from_html(cls, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]


class BunkrImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr.is Image Direct URL"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://cdn3.bunkr.is/2021-07-03-3024x4032_c87b68ca72e0b5296829cf1a9e187b2c-Km9gaCRc.jpg",
        "https://cdn3.bunkr.is/2021-07-03-3840x2880_9841c7b4aa6d1f96196660545973efa9-Kf5UfqsE.jpg",
        "https://cdn4.bunkr.is/2021-12-01-3024x4032_479bdb93acdb799bf81da5195ef0abf6-dFl47m7b.jpg",
        "https://cdn4.bunkr.is/2021-12-01-3023x4011_5f36416846cde7afd8b0f20f0835cb43-bFhLNQx2.jpg",
        "https://cdn3.bunkr.is/2022-02-03-3024x4032_55b5b85872dd4b7e76f988f4a4a3e70c-AIAQP0ju.jpg"
    ]

    def _extract_data(self, url):
        file_w_extension = url.split("/")[-1]
        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]


class BunkrArchiveExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr.is Archive direct link"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://cdn.bunkr.is/in-paris-NFp4EcUK.zip"
    ]

    def _extract_data(self, url):
        file_w_extension = url.split("/")[-1]
        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=url,
        )