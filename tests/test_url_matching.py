from unittest import TestCase
from scrapers import get_scraper_classes, ScraperType


def compose_html(urls: list) -> str:
    return "".join(
        [f'<a href="{url}" class="some random-class" ></a>'
         for
         url in urls]
    )


class UrlMatchingTest(TestCase):
    def test_url_matching(self):
        """
        Tests if each scraper matches input URLs it's supposed to match.
        """
        for scraper in get_scraper_classes(disabled_scrapers=[]):
            for url in scraper.SAMPLE_URLS:
                with self.subTest(scraper=scraper, url=url):
                    self.assertTrue(
                        scraper.is_suitable(url),
                        f"\n{scraper.__name__} FAILED TO MATCH: {url}"
                    )

    def test_html_url_extraction(self):
        """
        Tests if each extractor class is able to extract its URLs from given html.
        """
        for extractor in get_scraper_classes(
                disabled_scrapers=[],
                type_specific=ScraperType.EXTRACTOR):
            mock_html = compose_html(extractor.SAMPLE_URLS)
            extracted = extractor.extract_from_html(url="test", html=mock_html)

            for url in extractor.SAMPLE_URLS:
                with self.subTest(extractor=extractor, url=url):
                    self.assertIn(
                        url,
                        extracted,
                        msg=f"\n{extractor.__name__} failed to extract {url} from html."
                    )
