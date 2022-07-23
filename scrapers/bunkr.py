from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError
from utils import split_filename_ext
import logging
import re
import json

# Constant URLs
STREAM_URL = "https://media-files.bunkr.is"

# Regex Patterns
PATTERN_BUNKR_ALBUM = r"((?:https?://)?bunkr\.is/a/\w+)"
PATTERN_BUNKR_ALBUM_DATA_SCRIPT = r'<script id="__NEXT_DATA__" type="application/json">(\{.*?})</script>'
PATTERN_BUNKR_VIDEO = rf"((?:https?://)?stream\.bunkr\.is/v/[-\w\d]+?(?:{'|'.join(vid_extensions)}))"
# https://cdn3.bunkr.is/2021-07-03-3024x4032_c87b68ca72e0b5296829cf1a9e187b2c-Km9gaCRc.jpg
PATTERN_BUNKR_IMAGE = rf"((?:https://)?cdn\d+\.bunkr\.is/[-\d\w]+(?:{'|'.join(img_extensions)}))"


class BunkrAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr.is storage"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://bunkr.is/a/rXQtFw5W",
        "https://bunkr.is/a/jBCopZia",
        "https://bunkr.is/a/G6Mzbwpv",
        "https://bunkr.is/a/TCxaRKiw",
        "https://bunkr.is/a/XCIfbTX8"
    ]

    def _extract_data(self, url):
        response = self._request_page(
            url=url,
            headers={
                "Host": "bunkr.is"
            }
        )
        html = response.text

        # Extract the script that fetches album data in json format
        pattern = re.compile(PATTERN_BUNKR_ALBUM_DATA_SCRIPT)
        data_tag = re.search(pattern, html)

        if not data_tag:
            raise ExtractionError(
                f"{url}\n"
                f"Failed to extract data.\n"
                f"Didn't find html script tag containing data."
            )

        # Load into json
        json_ = json.loads(data_tag.group(1))
        is_fallback = json_["isFallback"]

        if json_ and is_fallback:
            raise ExtractionError(
                f"{url}\n"
                f"Failed to extract album data.\n"
                f"Data: {json_}\n"
                f"!'isFallback': True!"
            )

        album_data = json_["props"]["pageProps"]

        try:
            title = album_data['album']['name']
            files = album_data['files']
        except KeyError as e:
            raise ExtractionError(
                f"title = album_data['album']['name']\nfiles = album_data['files']\n"
                f"Failed extracting '{e}'\n"
                f"Data: {album_data}"
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

            if content_type == "image":
                source = f"{item['i']}/{file_w_extension}"
            elif content_type == "video":
                source = f"{STREAM_URL}/{file_w_extension}"
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

    @classmethod
    def _extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]


class BunkrVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "stream.bunkr.is"
    DESC = "Bunkr.is video page"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://stream.bunkr.is/v/ea_vid_14-9a9Jq32V.mov",
        "https://stream.bunkr.is/v/ea_vid_12-rlwMZzT1.mov",
        "https://stream.bunkr.is/v/lai_vid_3-3Ymk80tH.mp4",
        "https://stream.bunkr.is/v/rr_vid_12-3HiQTJtY.mp4",
        "https://stream.bunkr.is/v/ck_vid_9-m2OAY8pu.mp4"
    ]

    def _extract_data(self, url: str):
        file_w_extension = url.split("/")[-1]
        filename, extension = split_filename_ext(file_w_extension)

        content_type = determine_content_type_(extension)

        source = f"{STREAM_URL}/{file_w_extension}"

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )


class BunkrImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_BUNKR_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "bunkr.is"
    DESC = "Bunkr.is Image direct link"
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
    def _extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
