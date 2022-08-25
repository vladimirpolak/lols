from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json

PATTERN_EROME_ALBUM = r"(?:https://)?(www\.)erome\.com/a/\w+"


class EromeAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_EROME_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "erome.com"
    DESC = "Erome Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://www.erome.com/a/69MH41fn",
        "https://www.erome.com/a/srArB7Yt"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        print(response.status_code)
        print(response.headers)

        # self.add_item(
        #     content_type=content_type,
        #     filename=filename,
        #     extension=extension,
        #     source=source,
        #     album_title=album_title
        # )

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

# Images
# rf"(?:https://)?s\d+\.erome\.com/\d+/\w+/\w+(?:{'|'.join(img_extensions)})?v=\d+"
# https://s11.erome.com/981/69MH41fn/UwQFq07e.png?v=1661108453
# https://s11.erome.com/981/69MH41fn/F75mTh6A.png?v=1661108459
# https://s11.erome.com/981/69MH41fn/PQWXAKy4.png?v=1661108433
# https://s18.erome.com/902/srArB7Yt/wS1CDdpO.jpeg?v=1656038699
# https://s18.erome.com/902/srArB7Yt/ifzS65Qu.jpeg?v=1656038710
# https://s18.erome.com/902/srArB7Yt/xt8qX5r6.jpeg?v=1656038713
# https://s18.erome.com/902/srArB7Yt/w5ZZXRem.jpeg?v=1656038724
# https://s18.erome.com/902/srArB7Yt/cm1H6w5F.jpeg?v=1656038739


# Videos
# rf"(?:https://)?s\d+\.erome\.com/\d+/\w+/\w(?:{'|'.join(vid_extensions)})"
# https://s11.erome.com/981/69MH41fn/IXs23YUp_720p.mp4
# https://s18.erome.com/902/srArB7Yt/DTGmT1Qo_720p.mp4
# https://s18.erome.com/902/srArB7Yt/2CVMSZFc_720p.mp4
# https://s18.erome.com/902/srArB7Yt/BdusAg2n_720p.mp4
# https://s18.erome.com/902/srArB7Yt/jTleLhy9_720p.mp4
# https://s18.erome.com/902/srArB7Yt/GM8ueJ92_720p.mp4