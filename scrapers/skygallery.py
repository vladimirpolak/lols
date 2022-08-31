from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from utils import split_filename_ext
import logging
import re

SIASKY_DOMAIN = "https://siasky.net/"

PATTERN_SKYGALLERY_ALBUM = r"(?:https://)?skygallery\.hns\.siasky\.net/a/[-\w]+"


class SkygalleryExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_SKYGALLERY_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "skygallery.hns.siasky.net"
    DESC = "Skygallery File Hosting Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://skygallery.hns.siasky.net/a/AQBizutvay2Ll9_fEmrhkZBHPrmkVlGif4XC2hD2qcXiWg",
        "https://skygallery.hns.siasky.net/a/AQAaKj6xtDvz7BCBu47Ioval4NX7J2PQDxURBzopI6DnFw",
        "https://skygallery.hns.siasky.net/a/AQCKmONQJ5RhVvR8NRWmelZXD2JsqHndwJyha4VOIPq6cw"
    ]

    def _extract_data(self, url):
        album_id = url.split("/")[-1]

        json_data_link = SIASKY_DOMAIN + album_id
        response = self.request(
            url=json_data_link,
        )

        json = response.json()
        album_title = json["title"]
        data = json["files"]

        for item in data:
            # thumbnail_link = SIASKY_DOMAIN + item["skylinks"]["thumbnail"]

            fname_w_ext = item["filename"]  # 4ng3lm3lly_vid_2.mp4
            filename, extension = split_filename_ext(fname_w_ext)
            source = SIASKY_DOMAIN + item["skylinks"]["source"]
            content_type = determine_content_type_(extension)

            self.add_item(
                source=source,
                content_type=content_type,
                filename=filename,
                extension=extension,
                album_title=album_title
            )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

