from unittest import TestCase
from scrapers import get_scraper_classes


class UrlMatchingTest(TestCase):
    @property
    def scrapers(self):
        return get_scraper_classes()

    def test_patterns(self):
        for scraper in self.scrapers:
            for url in scraper.SAMPLE_URLS:
                self.assertTrue(scraper.is_suitable(url), f"{scraper.__name__} FAILED TO MATCH: {url}")
