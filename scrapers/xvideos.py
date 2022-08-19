from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json

# Constant URLs

# Regex Patterns
PATTERN_XVIDEOS_VIDEO = r"https?://(?:www\.)?xvideos\.com/video\d+/[\w\d]+"
PATTERN_XVIDEOS_VIDEOPAGE_INFOTAG = re.compile(r'<script type="application/ld\+json">((?s).*?)</script>')


class XvideosVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_XVIDEOS_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "xvideos.com"
    DESC = "Xvideos Video page"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://www.xvideos.com/video66403637/amateur_colombian_latina_teen_pov_blowjob_and_horny_sex_on_camera",
        "https://www.xvideos.com/video39997757/i_made_her_late_for_work_and_full_of_cum_epic_fuck_",
        "https://www.xvideos.com/video40596239/young_girl_gets_used_in_the_kitchen_before_class"
    ]

    def initialize(self):
        raise NotImplementedError()

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        match = re.findall(PATTERN_XVIDEOS_VIDEOPAGE_INFOTAG, html)
        if not match:
            raise ExtractionError(
                f"Error extracting video data from url: {url}"
            )
        try:
            data = json.loads(match[0])
        except Exception as e:
            print(e)
        # {
        #     "@context": "https://schema.org",
        #     "@type": "VideoObject",
        #     "name": "Amateur Colombian latina teen POV blowjob and horny sex on camera",
        #     "description": "Amateur Colombian latina teen POV blowjob and horny sex on camera",
        #     "thumbnailUrl": [
        #         "https://cdn77-pic.xvideos-cdn.com/videos_new/thumbs169ll/1f/b2/1b/1fb21b9bea3b672bff7d4930b48cccd2/1fb21b9bea3b672bff7d4930b48cccd2.18.jpg"],
        #     "uploadDate": "2021-11-09T10:57:04+00:00",
        #     "duration": "PT00H06M15S",
        #     "contentUrl": "https://video-hw.xvideos-cdn.com/videos_new/mp4/1/f/b/xvideos.com_1fb21b9bea3b672bff7d4930b48cccd2.mp4?e=1659232114&ri=1024&rs=85&h=8ac9372e2eafc79e6c7e281b69ab97fd",
        #     "interactionStatistic": {
        #         "@type": "InteractionCounter",
        #         "interactionType": {"@type": "WatchAction"},
        #         "userInteractionCount": 624740
        # }
        video_title = data["name"]
        source = data["contentUrl"]
        file_w_extension = source.split("?")[0].split("/")[-1]
        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type_(extension)

        self.add_item(
            content_type=content_type,
            filename=video_title,
            extension=extension,
            source=source,
            album_title="XVIDEOS"
        )

    # Extractor method only
    # @classmethod
    # def _extract_from_html(cls, html):
    #     return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
