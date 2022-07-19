from ._scraper_base import ExtractorBase
from downloader.types import determine_content_type_, img_extensions
from utils import split_filename_ext
import re

PATTERN_PIXL_ALBUM = r"((?:https?://)?pixl\.is/album/[-\d\w\.]+)"
PATTERN_PIXL_ALBUM_NAME = r'<a[\s\S]+data-text="album-name"[\s\S]+href="https://pixl.is/album/[-\d\w\.]+">(.*?)</a>'
PATTERN_PIXL_NEXT_PAGE = r'<a data-pagination="next"\s' \
                         r'href="(https://pixl\.is/album/{album_id}/\?page=\d+&seek=[\d-]+\+[\d(%3A)]+\.[\w\d]+)"'
PATTERN_PIXL_IMAGE = rf'((?:https?://)?i\.pixl\.is/[\w\d-]+\.md(?:{"|".join(img_extensions)}))'


class PixlAlbumExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_PIXL_ALBUM)
    PROTOCOL = "https"
    DOMAIN = "pixl.is"
    DESC = "Pixl Image Storage Album"
    CONTENT_TYPE = "ALBUM"
    SAMPLE_URLS = [
        "https://pixl.is/album/lena12.sb3Az"
    ]

    def _extract_data(self, url):
        pixl_album_id = url.split("/")[-1]
        all_html = ""

        while url:
            html, url = self._get_album_page(url, pixl_album_id)
            all_html = all_html + html

        album_name = self._extract_album_name(all_html)
        data = self._extract_images(all_html)

        for source in data:
            file = source.split("/")[-1]
            filename, extension = split_filename_ext(file)
            content_type = determine_content_type_(extension)

            self.add_item(
                content_type=content_type,
                filename=filename,
                extension=extension,
                source=source,
                album_title=album_name
            )

    def _get_album_page(self, url, album_id):
        response = self._request_page(
            url=url,
        )
        html = response.text

        # Get next page url
        pattern = re.compile(PATTERN_PIXL_NEXT_PAGE.format(album_id=album_id))
        result = pattern.findall(html)
        if result:
            next_page = result[0]
        else:
            next_page = None

        return html, next_page

    def _extract_images(self, html):
        urls = set(re.findall(PATTERN_PIXL_IMAGE, html, re.I))
        return [url.replace(".md.", ".") for url in urls]

    def _extract_album_name(self, html):
        pattern = re.compile(PATTERN_PIXL_ALBUM_NAME)
        result = pattern.search(html)
        try:
            album_name = result.group(1)
        except AttributeError:
            album_name = None
        return album_name
