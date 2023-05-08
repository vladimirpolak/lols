from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type
from ..exceptions import ExtractionError
from ..utils import split_filename_ext

import re
import base64
import urllib.parse

_CODENAME = "hex"
# Constant URLs
HEXUPLOAD_DOWNLOAD_URL = "https://hexupload.net/download"

# Regex Patterns
PATTERN_HEXUPLOAD = r"https://hexupload.net/[a-z\d]+"
VIDEO_ELEMENT = r'<source\s+' \
                r'src="(https://\d+\.contenthx\.me/d/\w+/video\.mp4)"' \
                r'\s+type="video/mp4">'


def decode_and_link_filename(link_encrypted: str, filename_encrypted: str) -> (str, str):
    return (
        base64.b64decode(link_encrypted).decode(),
        urllib.parse.unquote(base64.b64decode(filename_encrypted).decode('utf-8'))
    )


def create_payload_data(item_id: str) -> dict:
    return {
        "op": "download1",
        "id": item_id,
        "ajax": "1",
        "method_free": "1",
        "dataType": "json",
    }


def raise_status(status: str):
    status = status.upper()
    if not status == "OK":
        raise ExtractionError(
            f"Failed extracting data from Hexupload JSON, Status: '{status}'"
        )


class HexuploadVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_HEXUPLOAD)
    PROTOCOL = "https"
    DOMAIN = "hexupload.net"
    DESC = "Hexupload Hosting"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        item_id = url.split("/")[-1]
        response = self.request(
            method="POST",
            url=HEXUPLOAD_DOWNLOAD_URL,
            data=create_payload_data(item_id)
        )
        if not response.ok:
            raise ExtractionError(
                f"Failed accessing Hexupload JSON url for: '{url}' Status Code: '{response.status_code}'"
            )

        data_json = response.json()
        raise_status(data_json["status"])

        source, file_w_ext = self.extract_source_filename(data_json)

        filename, extension = split_filename_ext(file_w_ext)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    @classmethod
    def extract_source_filename(cls, data: dict) -> (str, str):
        try:
            source = data["link"]
            filename = data["file_name"]
        except KeyError:
            raise ExtractionError(
                f"Failed extracting data from Hexupload JSON (key/value pairs probably changed) Data: '{data}'"
            )
        else:
            return decode_and_link_filename(source, filename)
