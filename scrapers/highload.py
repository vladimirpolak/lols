from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext, decode_base64
import logging
import re
import json
# import js2py
# result = js2py.eval_js(script)

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
        vars_script = self._extract_vars_script(html)

        # prepare vars_script
        prepped_vars_script = self._prepare_script(vars_script)

        # get vars_script output with js2py
        # vars_script_output = js2py.eval_js(prepped_vars_script)

        # Request master.js
        master_script = self._get_masterjs(
            referer=url
        )

        # prepare master_script
        prepped_master_script = self._prepare_script(master_script)

        # get master_script output with js2py
        # master_script_output = js2py.eval_js(prepped_master_script)

        # extract source_variable, res_1 value and res_2 value
        # extract source_variable value from variables_script
        # decode the direct link based off values of source_variable, res_1 and res_2

        self._get_masterjs(referer=url)

    def _get_masterjs(self, referer: str):
        """Returns master.js script."""
        headers = {
            "referer": referer
        }
        response = self.request(
            url=URL_HIGHLOAD_MASTERJS,
            headers=headers
        )
        return response.text


    @staticmethod
    def _prepare_script(javascript: str):
        """
        Modifies the input javascript script so that the output is returned as a string.
        Removes the eval() function from the script and just calls the main function
        with its parameters. This way it returns the value and we can work with it going forward.
        """
        pattern = re.compile(
            r"(?P<first_half>.*)"
            r"eval\(function"
            r"(?P<main_func>.*})"
            r"(?P<main_params>\(.*)\)"
        )
        match = pattern.search(javascript)
        if not match:
            raise ValueError("Couldn't match regex.")

        first_half = match.group('first_half')
        main_func = match.group('main_func')
        main_params = match.group('main_params')
        return f"{first_half};function main {main_func};main{main_params}"

    @staticmethod
    def _extract_vars_script(html: str):
        pattern = re.compile(
            r'type="text/javascript">(?P<vars_script>var.*)</script'
        )
        result = pattern.search(html)
        if not result:
            raise ExtractionError()
        return result.group('vars_script')

    @staticmethod
    def _extract_source_var_name(javascript: str):
        pattern = re.compile(
            rf'var res = (\w+)\.replace'
        )
        match = pattern.search(javascript)
        if not match:
            raise ExtractionError()
        return match.group(1)

    @staticmethod
    def _decode_direct_link(source_var: str, res_1: str, res_2: str):
        return decode_base64(source_var.replace(res_1, "").replace(res_2, ""))

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
