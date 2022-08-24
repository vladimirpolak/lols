from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext, decode_base64
import logging
import re
import json

URL_HIGHLOAD_MASTERJS = "https://highload.to/assets/js/master.js"

PATTERN_HIGHLOAD_VIDEO = rf"(?:https://)?highload\.to/f/[a-z\d]+/[-\w]+(?:{'|'.join(vid_extensions)})"


class HighloadVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_HIGHLOAD_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "highload.to"
    DESC = "Highload Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://highload.to/f/rooptpwx3pog/Joey_Fisher_bath_nude_boobs_onlyfans_video.mp4",
        "https://highload.to/f/rvhuhxzpaioh/Joey_Fisher_2022-07-22_shower_onlyfans_video.mp4",
        "https://highload.to/f/mwa7i7yarcff/Joey_Fisher_8min_nude_onlyfans_video.mp4",
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        # extract vars_script
        # parse vars_script
        # get vars_script output with js2py

        # Request master.js
        # parse master_script
        # get master_script output with js2py

        # extract target_var, res_1 value and res_2 value
        # extract target_var value from variables_script
        # decode the direct link based off values of target_var, res_1 and res_2

        self._request_masterjs(referer=url)

    def _request_masterjs(self, referer: str):
        headers = {
            "referer": referer
        }
        response = self.request(
            url=URL_HIGHLOAD_MASTERJS,
            headers=headers
        )
        html = response.text
        print(html)
        exit()

    #     self.add_item(
    #         content_type=content_type,
    #         filename=filename,
    #         extension=extension,
    #         source=source,
    #         album_title=album_title
    #     )

    @staticmethod
    def _prepare_script(script: str):
        """
        Modifies the input javascript script so that the output is returned as a string.
        """
        pattern = re.compile(
            r"(?P<first_half>.*)"
            r"eval\(function"
            r"(?P<main_func>.*})"
            r"(?P<main_params>\(.*)\)"
        )
        match = pattern.search(script)
        if not match:
            raise ValueError("Couldn't match regex.")

        first_half = match.group('first_half')
        main_func = match.group('main_func')
        main_params = match.group('main_params')
        return f"{first_half};function main {main_func};main{main_params}"

    @staticmethod
    def _decode_direct_link(self):
        # var res = eddaacefaffd.replace("ZjEyZWFlNzlmMmFiZDUwMTY5NGYxODgzZjJiZDgwOGU", "");
        # var res2 = res.replace("NTQ5NmVlOWM1MTJmZjVhNGFiYzI4NWUwMTc0OTEyMTQ=", "");
        pass

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
