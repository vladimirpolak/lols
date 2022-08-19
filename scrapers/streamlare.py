from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
from exceptions import ExtractionError
from w3lib.html import replace_entities
from utils import split_filename_ext
import re
import json

# Constant URLs
GET_CONTENT_URL = "https://slwatch.co/api/video/download/get"

# Regex Patterns
PATTERN_STREAMLARE_VIDEO = r'(?:https://)?streamlare\.com/v/\w+'
PATTERN_STREAMLARE_DIRECTLINK_TAG = r'<video\s+' \
                                r'.*?' \
                                r'(src="https://larecontent\.com/video?token=[-\w\d]+)">'


class StreamlareVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_STREAMLARE_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "streamlare.com"
    DESC = "Streamlare Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://streamlare.com/v/0rwmD7pdJG1zRaZ8",
        "https://streamlare.com/v/j57gDmvpadez26Xb",
        "https://streamlare.com/v/Jj8GzOqr4e7nvPog",
        "https://streamlare.com/v/ZEvMDN5rEvQnNoKy",
        "https://streamlare.com/v/r8WdlWmq4dxDjx4q"
    ]

    def _extract_data(self, url):
        self.origin_url = url
        # raise NotImplementedError(self.__class__.__name__)
        response = self.request(
            url=self.origin_url,
        )
        html = response.text
        csrf_token = self._extract_csrf_token(html)
        video_info_str = self._extract_video_info_dict(html)
        video_info_dict = self._load_video_dict(video_info_str)

        file_w_extension = video_info_dict["name"]

        response = self.request(
            method='POST',
            url=GET_CONTENT_URL,
            headers={
                "origin": "https://slwatch.co",
                "referer": self.origin_url,
                "x-csrf-token": csrf_token,
                "x-requested-with": "XMLHttpRequest",
            },
            data={
                "id": url.split("/")[-1] if not url.endswith("/") else url[:-1].split("/")
            }
        )
        json_data = response.json()

        try:
            if not json_data["status"] == 'success':
                raise ExtractionError(f"Failed to extract data from: {url} RESPONSE_JSON: {json}")
            source = json_data["result"]["Original"]["url"]
        except KeyError:
            raise ExtractionError(f"Failed to extract data from: {url} RESPONSE_JSON: {json}")

        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source,
        )

    def _extract_csrf_token(self, html):
        pattern = re.compile(
            r'<meta\s+name="csrf-token"\s+content="(?P<csrf_token>[a-zA-Z\d]+)">'
        )
        match = pattern.search(html)
        if match:
            return match.group('csrf_token')
        else:
            raise ExtractionError(
                f"Failed to extract csrf token from: {self.origin_url}"
            )

    def _extract_video_info_dict(self, html):
        pattern = re.compile(
            r'<file-video\s+:file="(?P<info_dict>.*)" :config.*"></file-video>'
        )
        match = pattern.search(html)
        if match:
            return match.group('info_dict')
        else:
            raise ExtractionError(
                f"Failed to extract video info dictionary from: {self.origin_url}"
            )

    def _load_video_dict(self, info_dict_str):
        """
        Output dict example:
        {
        'hashid': '0rwmD7pdJG1zRaZ8',
        'mimeType': 'video/mp4',
        'size': 490490250,
        'name': 'officialheimi-XeYIy3Nw.mp4',
        'status': 'converted',
        'created_at':
        '2022-08-12T03:15:04.000000Z'
        }
        """
        unescaped = replace_entities(info_dict_str)
        return json.loads(unescaped)

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
