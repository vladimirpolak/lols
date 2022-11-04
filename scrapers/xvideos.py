from exceptions import ExtractionError
from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_
import re

# Regex Patterns
PATTERN_XVIDEOS_VIDEO = r"https?://(?:www\.)?xvideos\.com/video\d+/[\w\d]+"
PATTERN_XVIDEOS_TITLE = r'<meta property="og:title" content="(?P<title>.*?)"\s?/>'
PATTERN_XVIDEOS_STREAMURL = r"html5player\.setVideoHLS\('(?P<stream_url>.*?)'\)"


class XvideosVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_XVIDEOS_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "xvideos.com"
    DESC = "Xvideos Video page"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://www.xvideos.com/video47959115/sexy_bitch_koketochka555_masturbates_on_camera_and_shows_tits",
        "https://www.xvideos.com/video66403637/amateur_colombian_latina_teen_pov_blowjob_and_horny_sex_on_camera",
        "https://www.xvideos.com/video39997757/i_made_her_late_for_work_and_full_of_cum_epic_fuck_",
        "https://www.xvideos.com/video40596239/young_girl_gets_used_in_the_kitchen_before_class"
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
            source=source
        )

    def _extract_video_info(self, html):
        stream_url = self._extract_stream_url(html)
        title = self._extract_title(html)
        return title, stream_url

    def _extract_stream_url(self, html):
        pattern = re.compile(r"html5player\.setVideoHLS\('(?P<stream_url>.*?)'\)")
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
    def _extract_from_html(cls, html):
        # return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
        pass
