from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, vid_extensions
from exceptions import ExtractionError
from utils import split_filename_ext, decode_base64
import re
import js2py


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
        self.origin_url = url
        response = self.request(
            url=self.origin_url,
        )
        html = response.text

        # extract vars_script
        vars_script = self._extract_vars_script(html)
        # prepare vars_script
        prepped_vars_script = self._prepare_script(vars_script)
        # get vars_script output with js2py
        vars_script_output = js2py.eval_js(prepped_vars_script)

        # Request master.js
        master_script = self._get_masterjs(
            referer=self.origin_url
        )

        # prepare master_script
        prepped_master_script = self._prepare_script(master_script)
        # get master_script output with js2py
        master_script_output = js2py.eval_js(prepped_master_script)
        # extract source_variable, res_1 value and res_2 value
        source_var = self._extract_source_var_name(master_script_output)
        res_1, res_2 = self._extract_res1_res2(master_script_output)

        # extract source_variable value from variables_script
        source_value = self._extract_source_var_value(
            javascript=vars_script_output,
            var_name=source_var
        )
        # decode the direct link based off values of source_variable, res_1 and res_2
        source = self._decode_direct_link(
            source_value, res_1, res_2
        )

        file_w_ext = self.origin_url.split("/")[-1]
        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type_(extension)

        self.add_item(
            source=source,
            filename=filename,
            extension=extension,
            content_type=content_type
        )

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
        result = pattern.search(javascript)
        if not result:
            raise ValueError("Couldn't match regex.")

        first_half = result.group('first_half')
        main_func = result.group('main_func')
        main_params = result.group('main_params')
        return f"{first_half};function main {main_func};main{main_params}"

    @staticmethod
    def _extract_vars_script(html: str):
        pattern = re.compile(
            r'type="text/javascript">(?P<vars_script>var.*)</script'
        )
        result = pattern.search(html)
        if not result:
            raise ExtractionError("Failed to extract 'vars_script'.")
        return result.group('vars_script')

    @staticmethod
    def _extract_source_var_name(javascript: str):
        pattern = re.compile(
            rf'var res = (\w+)\.replace'
        )
        result = pattern.search(javascript)
        if not result:
            raise ExtractionError("Failed to extract source variable name from 'master.js'.")
        return result.group(1)

    @staticmethod
    def _extract_source_var_value(javascript: str, var_name: str):
        pattern = re.compile(
            rf'var {var_name}[\s=]+"(.*?)";'
        )
        result = pattern.search(javascript)
        if not result:
            raise ExtractionError(f"Failed to extract source value from vars_script, source var: {var_name}")
        return result.group(1)

    @staticmethod
    def _extract_res1_res2(javascript: str):
        pattern = re.compile(
            rf'var res[\s=]+(\w+)\.replace\("(?P<res_1>.*?)"[\s,"]+\);?\s*'
            rf'var res2[\s=]+res\.replace\("(?P<res_2>.*?)"[\s,"]+\);'
        )
        result = pattern.search(javascript)
        if not result:
            raise ExtractionError("Failed to extract res variables from 'master.js'.")
        return result.group('res_1'), result.group('res_2')

    @staticmethod
    def _decode_direct_link(source_var: str, res_1: str, res_2: str):
        return decode_base64(source_var.replace(res_1, "").replace(res_2, ""))

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
