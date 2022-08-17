from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
import logging
import re
import json


# Request URL: https://adblockeronstape.me/get_video?id=L280lgyDKWfa82&expires=1660760175&ip=GxMsDRSAKxSHDN&token=NgrscXNPTAMP&stream=1
# Request Method: GET
# Status Code: 302
# Remote Address: 188.114.97.3:443
# Referrer Policy: strict-origin-when-cross-origin
# access-control-allow-origin: *
# alt-svc: h3=":443"; ma=86400, h3-29=":443"; ma=86400
# cache-control: private
# cf-cache-status: DYNAMIC
# cf-ray: 73bdbaf249b9c31d-VIE
# content-type: video/mp4
# date: Tue, 16 Aug 2022 22:50:40 GMT
# expect-ct: max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"
# location: https://868418908.tapecontent.net/radosgw/L280lgyDKWfa82/4i2mq9eCBDfc3gpKzNMOxNfE79dNmVkGWTiCcsHeGfWV3r2yI4dvGkIbw11cbK-z9_hhg9UFweDy0sKvu-TToXRj9xlz8xPwdZBGyye1MiFh5WNwoS_OYzg8LBh33l5g2-SIZuy7gFdNjinbVHGoNaQBh2sZQxPzsxDAy0UcRFfx91Jv4KJcN5ZJDHVJ9-slNp7Im4-S3cBfEo38-cbgiyxZmCmNtLpvSzVavhcBfV-jZXV4CQL4nsopVfjB7F76xGFNTHQGah4J2T-jnhWib8Uh2JI0x1CF0qv8OVogu1zxpDF9hvBTTZnTZtU/Lauren+Alexis+Fuck+Me+Daddy+Video+Leaked.mp4?stream=1
# nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
# report-to: {"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v3?s=%2B1S2AJIOFu01Jdc5E6TNHt5aDoYHjQdCy1vFcDvRlahf%2FwSVi9PbVg1i5BsY%2FWWPkhCMb1Nx1lQBIHVqB4dKI5Z1dyvHr3X0CS7kzjS0srypGOwnWhmFiafDqtmGlAzlE5w%2Binlb"}],"group":"cf-nel","max_age":604800}
# server: cloudflare
# :authority: adblockeronstape.me
# :method: GET
# :path: /get_video?id=L280lgyDKWfa82&expires=1660760175&ip=GxMsDRSAKxSHDN&token=NgrscXNPTAMP&stream=1
# :scheme: https
# accept: */*
# accept-encoding: identity;q=1, *;q=0
# accept-language: en-US,en;q=0.9,sk;q=0.8
# cookie: _csrf=406aacf195686f0b802dd829d37e15ecc724e88ab5676b99b3cee3f318a6d2cca%3A2%3A%7Bi%3A0%3Bs%3A5%3A%22_csrf%22%3Bi%3A1%3Bs%3A32%3A%22fElXKmvZNUcyD0llDSDCy9EU1vgayJU1%22%3B%7D; _b=kube12; _popfired=1; _popfired_expires=Wed%2C%2017%20Aug%202022%2022%3A43%3A36%20GMT; lastOpenAt_=1660689816428
# range: bytes=0-
# referer: https://adblockeronstape.me/v/L280lgyDKWfa82/Lauren_Alexis_Fuck_Me_Daddy_Video_Leaked.mp4
# sec-ch-ua: "Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"
# sec-ch-ua-mobile: ?0
# sec-ch-ua-platform: "Windows"
# sec-fetch-dest: video
# sec-fetch-mode: cors
# sec-fetch-site: same-origin
# sec-gpc: 1
# user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36


URL_STREAMTAPE_GETVIDEO = "https://adblockeronstape.me/"

PATTERN_STREAMTAPE_VIDEO = rf'(?:https://)streamtape\.com/v/[a-zA-Z\d]+/[-\w\d]+({"|".join(vid_extensions)})'
PATTERN_STREAMTAPE_DIRECTURL_INFO = r'get_video\?id=[a-zA-Z\d]+&expires=\d+&ip=[a-zA-Z\d]+&token=[a-zA-Z\d]+'


class StreamtapeVideoExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_STREAMTAPE_VIDEO)
    PROTOCOL = "https"
    DOMAIN = "streamtape.com"
    DESC = "Streamtape Video Hosting"
    CONTENT_TYPE = "ITEM"
    SAMPLE_URLS = [
        "https://streamtape.com/v/L280lgyDKWfa82/Lauren_Alexis_Fuck_Me_Daddy_Video_Leaked.mp4"
    ]

    def _extract_data(self, url):
        response = self.request(
            url=url,
        )
        html = response.text
        source = self._extract_directurl(html)
        print(source)
        exit()

        # self.add_item(
        #     content_type=content_type,
        #     filename=filename,
        #     extension=extension,
        #     source=source,
        #     album_title=album_title
        # )

    def _extract_directurl(self, html):
        result = re.findall(PATTERN_STREAMTAPE_DIRECTURL_INFO, html)
        if result:
            return URL_STREAMTAPE_GETVIDEO + result[0]
        else:
            return None

    @classmethod
    def extract_from_html(cls, html):
        return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

    # Crawler method only
    # def _crawl_link(self, url) -> html[str]:
    #     pass
