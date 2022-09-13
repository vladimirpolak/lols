from unittest import TestCase
from scrapers import get_scraper_classes


class UrlMatchingTest(TestCase):
    def test_patterns(self):
        scraper_classes = get_scraper_classes()
        for scraper in scraper_classes:
            for url in scraper.SAMPLE_URLS:
                self.assertTrue(scraper.is_suitable(url), f"{scraper.__name__} FAILED TO MATCH: {url}")
