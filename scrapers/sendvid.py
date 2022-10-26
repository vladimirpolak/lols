from exceptions import ExtractionError
from scrapers._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
import re

# Regex Patterns
PATTERN_SENDVIDEO_VIDEOPAGE = r"https://sendvid\.com/[a-z\d]"


class SendvideoVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_SENDVIDEO_VIDEOPAGE)
    PROTOCOL = "https"
    DOMAIN = "sendvideo.com"
    DESC = "SendVideo Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://sendvid.com/7ocshpp8",
        "https://sendvid.com/m2fufq8h",
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text

        filename, source = self._extract_video_info(html)

        self.add_item(
            content_type=determine_content_type_('m3u8'),
            filename=filename,
            extension="",
            source=source,
        )

    def _extract_video_info(self, html):
        url = self._extract_stream_url(html)
        title = self._extract_title(html)
        return title, url

    def _extract_stream_url(self, html):
        pattern = re.compile(r'<source src="(?P<stream_url>.*?)"\s+.*?id="video_source"/>')
        result = pattern.search(html)
        if not result:
            raise ExtractionError("Failed to extract hls stream from html.")
        return result.group("stream_url")

    def _extract_title(self, html):
        pattern = re.compile('<meta property="og:title" content="(?P<title>.*?)"\s?/>')
        result = pattern.search(html)
        if not result:
            raise ExtractionError("Failed to extract title from html.")
        return result.group("title")

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

    # Crawler method only
    # def _crawl_link(self, url) -> html[str]:
    #     pass
