from ._scraper_base import ExtractorBase
from ..http.types import determine_content_type
from ..utils import split_filename_ext, slugify
from ..exceptions import ExtractionError

import re

_CODENAME = "anon"

# Regex Patterns
PATTERN_ANONFILES = r"(?:https?://)?anonfiles\.com/[-/\w]+"
PATTERN_ANONFILES_DLTAG = re.compile(r'(?s)"download-url".*?href="(.*?)">')
# In this modified pattern, the (?s) syntax at the beginning of the pattern specifies the re.DOTALL flag,
# which allows the . metacharacter to match any character, including newlines.


class AnonfilesExtractor(ExtractorBase):
    VALID_URL_RE = re.compile(PATTERN_ANONFILES)
    PROTOCOL = "https"
    DOMAIN = "anonfiles.com"
    DESC = "AnonFiles File Storage"
    CODENAME = _CODENAME

    def _extract_data(self, url):
        # Get the page
        response = self.request(
            url=url,
        )
        if not response.ok:
            raise ExtractionError(f"Failed to access '{url}'. Response code '{response.status_code}'.")
        html = response.text

        source = self._extract_download_url(html, url)

        # Parse the data
        file = source.split("/")[-1]
        filename, extension = split_filename_ext(file)
        filename = slugify(filename, replace_entities=True, del_special_chars=True)
        content_type = determine_content_type(extension)

        # Add item to output
        self.add_item(
            content_type=content_type,
            filename=filename,
            extension=extension,
            source=source
        )

    def _extract_download_url(self, html: str, origin_url: str):
        result = re.findall(PATTERN_ANONFILES_DLTAG, html)
        if not result:
            raise ExtractionError(f"Failed to extract download url from: {origin_url}")
        return result.pop()
