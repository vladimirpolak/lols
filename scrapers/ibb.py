from exceptions import ExtractionError
from ._scraper_base import ExtractorBase
from typing import Union
from utils import split_filename_ext, url_params_to_dict
from urllib.parse import unquote, urlencode
from downloader.types import determine_content_type_
import logging
import re
import json

# Constant URLs
IBB_JSON_URL = "https://ibb.co/json"

# Regex Patterns
PATTERN_IBB_ALBUM = r"(?:https://)?ibb\.co[/]+?album[/]+?(?:[a-zA-Z0-9]+?)"
PATTERN_IBB_AUTH_TOKEN = r'PF\.obj\.config\.auth_token="(?P<auth_token>.+?)";'
PATTERN_IBB_DATA_STRING = r"data-object='(?P<data>.*)'>"
PATTERN_IBB_NEXT_PAGE = r'data-pagination="next" href="(?P<next_page_url>.*?)">'


def ibb_json_payload(page_num, album_id, seek_id, auth_token):
    return {
        'action': 'list',
        'list': 'images',
        'sort': 'date_desc',
        'page': page_num,
        'from': 'album',
        'albumid': album_id,
        'params_hidden[list]': 'images',
        'params_hidden[from]': 'album',
        'params_hidden[albumid]': album_id,
        'seek': seek_id,
        'auth_token': auth_token,
    }


def ibb_json_headers(query_string: str, album_url: str):
    return {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "origin": "https://ibb.co",
        "content-length": str(len(query_string)),
        "referer": album_url
    }


class IBBExtractor(ExtractorBase):
    NEXT_PAGE = None
    VALID_URL_RE = re.compile(PATTERN_IBB_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "ibb.co"
    DESC = "IBB Album Extractor"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://ibb.co/album/j6FBxt",
        "https://ibb.co/album/67dBTK"
    ]

    def _extract_data(self, url):
        self.album_id = url.split("/")[-1]
        response = self.request(
            url=url,
        )
        html = response.text
        self._real_extract(html, url)

    def _real_extract(self, html: str, album_url: str):
        self._extract_items_info(html)

        # # Get album title
        # title = soup.find('a', {'data-text': 'album-name'}).text.strip()
        # self.title = title

        auth_token = self._extract_auth_token(html)
        np_info = self._extract_next_page_info(html)
        if np_info:
            next_page_num = int(np_info["page"])
            next_seek_id = np_info["seek"]

            while next_page_num and next_seek_id:
                json_payload = ibb_json_payload(
                    page_num=str(next_page_num),
                    album_id=self.album_id,
                    seek_id=next_seek_id,
                    auth_token=auth_token
                )
                headers = {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "origin": "https://ibb.co",
                    "content-length": str(len(urlencode(json_payload))),
                    "referer": album_url
                }
                res = self.request(method="POST", url=IBB_JSON_URL, data=json_payload, headers=headers)
                data = res.json()
                status = data["status_code"]
                logging.debug(f"IBB Json status: {status}")

                next_seek_id = data["seekEnd"]
                next_page_num += 1

                data_html = data["html"]
                self._extract_items_info(data_html)

    def _extract_items_info(self, html: str):
        results = re.findall(PATTERN_IBB_DATA_STRING, html)
        data = [json.loads(unquote(item)) for item in results]
        for item in data:
            self._parse_item(item)

    def _parse_item(self, item_dict: dict):
        try:
            source = item_dict['image']['url']
            filename, extension = split_filename_ext(item_dict['image']['filename'])
            # thumbnail = item_dict['medium']['url']
        except KeyError:
            logging.error(f"Error parsing IBB item data: {item_dict}")
        else:
            content_type = determine_content_type_(extension)
            self.add_item(
                content_type=content_type,
                filename=filename,
                extension=extension,
                source=source,
            )

    @staticmethod
    def _extract_auth_token(html: str) -> str:
        match = re.search(PATTERN_IBB_AUTH_TOKEN, html)
        if not match:
            raise ExtractionError("Failed to extract authorization token.")
        return match.group("auth_token")

    @staticmethod
    def _extract_next_page_info(html: str) -> Union[dict, None]:
        match = re.search(PATTERN_IBB_NEXT_PAGE, html)
        if not match:
            return None

        params_dict = url_params_to_dict(match.group("next_page_url").split("?")[-1])
        if not params_dict:
            raise ExtractionError("Failed parsing URL params.")

        return params_dict

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

