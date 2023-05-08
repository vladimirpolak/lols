from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type, img_extensions
from ..exceptions import ExtractionError
from ..utils import split_filename_ext

import logging
import re

_CODENAME = "jpgchurch"

# Regex Patterns
PATTERN_JPEGCHURCH_ALBUM = r"(?:https?://)?jpg\.(?:church|fish|fishing)/a/[-\w]+?\.[a-zA-Z]+"
PATTERN_JPEGCHURCH_NEXT_PAGE_TAG = r'<a\sdata-pagination="next"\s' \
    r'href="' \
    r'(https://jpg\.(?:church|fish|fishing)/a/{album_id}/\?page=\d+?&seek=(?:\d+-?)+\+(?:\d+(?:%3A)?)+\.\w+)' \
    r'"\s*>'
PATTERN_JPEGCHURCH_IMAGE = rf'((?:https?://)?simp\d+\.jpg\.(?:church|fish|fishing)/[-/\w]+?(?:.md)?(?:{"|".join(img_extensions)}))'


class JPGChurchExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_JPEGCHURCH_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "jpg.church"
    DESC = "JpegChurch Image Album"
    CODENAME = _CODENAME

    def _extract_data(self, url: str):
        # Album name from url
        self.jpegchurch_album_id = url.split("/")[-1]

        all_pages_html = ""

        while url:
            html, url = self._get_album_page(url)
            all_pages_html = all_pages_html + html

        try:
            urls = self._extract_content_links(all_pages_html)
        except Exception as e:
            raise ExtractionError(
                f"{e}\n"
                f"{url}\n"
                f"Failed to extract data."
            )

        for url in urls:
            source = url.replace(".md.", ".")
            file_w_extension = source.split("/")[-1]
            filename, extension = split_filename_ext(file_w_extension)
            content_type = determine_content_type(extension)

            self.add_item(
                source=source,
                content_type=content_type,
                filename=filename,
                extension=extension,
                album_title=self.jpegchurch_album_id
            )

    def _get_album_page(self, url):
        response = self.request(url)
        html = response.text

        next_page = self._next_page(html)

        return html, next_page

    def _extract_content_links(self, html):
        """Extract image links from the album html."""
        return set(re.findall(PATTERN_JPEGCHURCH_IMAGE, html, re.I))

    def _next_page(self, html):
        """Extract next page url."""
        pattern = re.compile(PATTERN_JPEGCHURCH_NEXT_PAGE_TAG.format(album_id=self.jpegchurch_album_id))
        try:
            match = pattern.search(html)
            next_page = match.group(1)
            if next_page:
                logging.debug(f"NEXT PAGE: {next_page}")
        except AttributeError:
            return None
        else:
            return next_page


class JPGChurchImageExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_JPEGCHURCH_IMAGE)
    PROTOCOL = "https"
    DOMAIN = "simp[0-9].jpeg.church"
    DESC = "JpegChurch Image Link"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        source = url.replace(".md.", ".")
        file_w_extension = source.split("/")[-1]
        filename, extension = split_filename_ext(file_w_extension)
        content_type = determine_content_type(extension)

        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )
