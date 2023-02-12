from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type
from exceptions import ExtractionError
from utils import split_filename_ext, decode_base64
import re
import json

# Constant URLs

PATTERN_VOE = r"(?:https://)?voe\.sx/\w+"


class VOEVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_VOE)
    PROTOCOL = "https"
    DOMAIN = "voe.sx"
    DESC = "Voe Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://voe.sx/h1a8w3ymf7r1",
        "https://voe.sx/k2zr0wrd2lg1",
        "https://voe.sx/x8oyxou115uz"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        source = self._extract_direct_url(html, url)
        content_type = determine_content_type(source)

        title = self._extract_title(html)
        if not title:
            filename = url.split("/")[-1]
        else:
            filename = title
        _, extension = split_filename_ext(source)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _extract_direct_url(self, html, origin_url):
        obfuscated = self._extract_obfuscated_url(html)
        if not obfuscated:
            raise ExtractionError(f"Failed to extract obfuscated url: {origin_url}")

        direct_url = self._deobfuscate_url(obfuscated)
        if not direct_url:
            raise ExtractionError(f"Failed to deobfuscate url from: {obfuscated}, ORIGIN_URL: {origin_url}")

        return direct_url

    def _extract_obfuscated_url(self, html):
        p = re.compile(
            r'sources\["mp4"]\s+=\s+[a-z\d]+\((.*)\);'
        )
        result = p.findall(html)
        try:
            list_string = result[0]
        except IndexError:
            return None
        else:
            return json.loads(list_string.replace('\'', '"'))

    def _deobfuscate_url(self, obfuscated):
        char_string = "".join(obfuscated)
        separated_chars_list = [*char_string]
        separated_chars_list.reverse()
        base64_string = "".join(separated_chars_list)
        return decode_base64(base64_string)

    def _extract_title(self, html):
        p = re.compile(
            r'<title>Watch\s+(.*)</title>'
        )
        result = p.findall(html)
        try:
            title = result[0]
            return title.replace(
                ' ', '-'
            )
        except IndexError:
            return None

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
