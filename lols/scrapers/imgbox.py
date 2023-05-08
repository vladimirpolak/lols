import logging

from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type, img_extensions
from ..utils import split_filename_ext
from ..exceptions import ExtractionError

import re

_CODENAME = "imgbox"

# Regex Patterns
PATTERN_IMGBOX_IMAGE_TH = rf"((?:https?://)?(?:thumbs|images)\d+\.imgbox\.com/[a-z\d]+/[a-z\d]+/[\w]+(?:_t|_o)(?:{'|'.join(img_extensions)}))"
PATTERN_IMGBOX_IMAGE_INDIRECT = r'(?:https?://)?imgbox\.com/\w+'


class IMGBoxImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMGBOX_IMAGE_INDIRECT)
    PROTOCOL = "https"
    DOMAIN = 'imgbox.com'
    DESC = 'ImgBox indirect Image url'
    CODENAME = _CODENAME

    def _extract_data(self, url: str):
        res = self.request(url)
        html = res.text
        self._parse_url(self._extract_direct_url(html))

    def _extract_direct_url(self, html: str) -> str:
        pattern = re.compile('(?:https?://)?images\d*\.imgbox\.com[./\w]+')
        match = re.search(pattern, html)
        logging.debug(match)
        if match:
            return match.group(0)
        raise ExtractionError("Failed to extract direct link from html.")

    def _parse_url(self, image_url: str):
        filename_w_ext = image_url.split("/")[-1]
        filename, ext = split_filename_ext(filename_w_ext)
        content_type = determine_content_type(ext)

        self.add_item(
            source=image_url,
            filename=filename,
            extension=ext,
            content_type=content_type,

        )


class IMGBoxThumbnailToImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_IMGBOX_IMAGE_TH)
    PROTOCOL = "https"
    DOMAIN = "imgbox.com"
    DESC = "ImgBox Extract From Thumbnail"
    CONTENT_TYPE = "ITEM"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        source = url.replace(
            "thumbs", "images", 1
        ).replace(
            "_t.", "_o.", 1
        )
        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        content_type = determine_content_type(extension)

        self.add_item(
            source=source,
            content_type=content_type,
            filename=filename,
            extension=extension
        )
