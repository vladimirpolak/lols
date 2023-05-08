from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type, vid_extensions
from ..exceptions import ExtractionError
from ..utils import split_filename_ext, decode_base64

from ast import literal_eval as make_tuple

import math
import re

_CODENAME = "hload"

URL_HIGHLOAD_MASTERJS = "https://highload.to/assets/js/master.js"

PATTERN_HIGHLOAD_VIDEO = re.compile(rf"(?:https://)?highload\.to/f/[a-z\d]+(?:/[-\w.%]+(?:{'|'.join(vid_extensions)}))?")


def master_script(h, u, n, t, e, r):
    def _0xe59c(d, e, f):
        g = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/')
        h = g[:e]
        i = g[:f]
        j = sum([h.index(b) * (math.pow(e, c)) for c, b in enumerate(reversed(list(d))) if b in h])
        k = ''
        while j > 0:
            k = i[int(j % f)] + k
            j = (j - (j % f)) / f
        return k or '0'

    def translate_function(h, u, n, t, e, r=None):
        r = ""
        i = 0
        while i < len(h):
            s = ""
            while i < len(h) and h[i] != n[e]:
                s += h[i]
                i += 1
            i += 1
            for j in range(len(n)):
                s = re.sub(re.compile(n[j], re.MULTILINE), str(j), s)
            r += chr(int(_0xe59c(s, e, 10)) - t)
        return r.encode('iso-8859-1').decode('utf-8')
    return translate_function(h, u, n, t, e, r)


def variables_script(h, u, n, t, e, r):
    def _0xe20c(d, e, f):
        g = list('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+/')
        h = g[:e]
        i = g[:f]
        j = sum([h.index(b) * (math.pow(e, c)) for c, b in enumerate(reversed(list(d))) if b in h])
        k = ''
        while j > 0:
            k = i[int(j % f)] + k
            j = (j - (j % f)) / f
        return k or '0'

    def translate_function_2(h, u, n, t, e, r=None):
        r = ""
        i = 0
        while i < len(h):
            s = ""
            while i < len(h) and h[i] != n[e]:
                s += h[i]
                i += 1
            i += 1
            for j in range(len(n)):
                s = re.sub(re.compile(n[j], re.MULTILINE), str(j), s)
            r += chr(int(_0xe20c(s, e, 10)) - t)
        return r.encode('iso-8859-1').decode('utf-8')
    return translate_function_2(h, u, n, t, e, r)


class HighloadVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_HIGHLOAD_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "highload.to"
    DESC = "Highload Video Hosting"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        if not response.ok:
            raise ExtractionError(f"Failed to access: '{url}' Status_Code: {response.status_code}")

        html = response.text

        vars_script = self.get_vars_script(html)
        master_script = self.get_master_script(origin=url)

        source = self.generate_direct_link(vars_script, master_script)
        file_w_ext = url.split("/")[-1]
        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type(extension)

        self.add_item(
            source=source,
            filename=filename,
            extension=extension,
            content_type=content_type,
        )

    def get_vars_script(self, html):
        # extract vars_script
        vars_script_encrypted = self._extract_vars_script(html)
        # get vars_script parameters
        parameters = self._extract_script_params(vars_script_encrypted)
        return variables_script(*parameters)

    def get_master_script(self, origin: str):
        # Request master.js
        master_script_encrypted = self._get_masterjs(
            referer=origin
        )
        # get master_script parameters
        parameters = self._extract_script_params(master_script_encrypted)
        return master_script(*parameters)

    def generate_direct_link(self, vars_script, master_script):
        # extract source_variable, res_1 value and res_2 value
        source_var = self._extract_source_var_name(master_script)
        res_1, res_2 = self._extract_res1_res2(master_script)

        # extract source_variable value from variables_script
        source_value = self._extract_source_var_value(
            javascript=vars_script,
            var_name=source_var
        )
        # decode the direct link based off values of source_variable, res_1 and res_2
        return self._decode_direct_link(
            source_value, res_1, res_2
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
    def _extract_script_params(javascript: str) -> tuple:
        """
        Extracts the input parameters for decoder function.
        """
        pattern = re.compile(
            r"(?P<first_half>.*)"
            r"eval\(function"
            r"(?P<main_func>.*})"
            r"(?P<main_params>\(.*)\)"
        )
        result = pattern.search(javascript)
        if not result:
            raise ExtractionError("Hexupload javascript couldn't match regex.")

        main_params = result.group('main_params')
        return make_tuple(main_params)

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
