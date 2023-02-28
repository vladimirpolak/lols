from downloader.types import ContentType
from ._scraper_base import ExtractorBase
from random import randint
import requests
import retry
import logging
import re

_CODENAME = "mega"

# Constant URLs
MEGA_API_CHECK_STATUS_URL = 'https://g.api.mega.co.nz/cs'

# Regex Patterns
MEGA_CONTENT_URL_RE = re.compile(r"(?P<url>(?:https://)mega\.nz(?:/(?P<url_type>folder|file)\/(?P<content_id>[-\w\d#]+))+)")


class MegaNZExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(MEGA_CONTENT_URL_RE)
    PROTOCOL = "https"
    DOMAIN = "mega.nz"
    DESC = "Mega.nz File Hosting (download not supported)"
    CONTENT_TYPE = None
    CODENAME = _CODENAME
    SAMPLE_URLS = [
        "https://mega.nz/folder/ITkSVDbY#uF8L36gsmHi8ETyHRir4aw",
        "https://mega.nz/folder/bnhCFJyB#Y401NT75fMJjIOIRKRECmA",
        "https://mega.nz/folder/w3RGFR6Z#GYNDMeivPMnXNaSYnGB73w/folder/JyJUFDIa",
        "https://mega.nz/folder/y8QwnDqK#v5hHiFt8STAwoibEdh0Xww/folder/304Gza5R",
        "https://mega.nz/folder/ll0yUBAB#IrWiSaAiQ5174lvst7twGQ",
    ]

    def _extract_data(self, url: str, check_is_alive: bool = True):
        is_alive = False
        if check_is_alive:
            if self._is_alive(url):
                is_alive = True
                logging.debug(f'ALIVE {url}')
            else:
                is_alive = False
                logging.debug(f'DEAD {url}')

        if (check_is_alive and is_alive) or not check_is_alive:
            self.add_item(
                content_type=ContentType.URL,
                filename="",
                extension="",
                source=url,
            )

    @retry.retry(requests.exceptions.JSONDecodeError, tries=3, delay=3)
    def _is_alive(self, url: str) -> bool:
        """
        Thanks to https://github.com/basisvectors for his mega link checker.

        https://github.com/basisvectors/mega-checker
        """
        parsed_url = self.VALID_URL_RE.match(url)
        content_id = parsed_url.group('content_id').split('#')[0]
        url_type = parsed_url.group('url_type')

        data = self._prep_req_data(url_type, content_id)
        params = {
            'id': ''.join(["{}".format(randint(0, 9)) for _ in range(0, 10)]),
            'n': content_id
        }

        res = self.request(method='POST', url=MEGA_API_CHECK_STATUS_URL, params=params, data=data)
        return res.json() == -2

    @staticmethod
    def _prep_req_data(url_type: str, content_id) -> dict:
        return {
            'folder': {"a": "f", "c": 1, "r": 1, "ca": 1},
            'file': {"a": 'g', "p": content_id}
        }[url_type]

    @classmethod
    def extract_from_html(cls, url, html):
        return [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]

