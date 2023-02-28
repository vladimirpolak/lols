import unittest
from scrapers import (get_scraper_classes,
                      ScraperType,
                      ExtractorBase,
                      ScraperBase,
                      CrawlerBase)


class ScraperFetchingTest(unittest.TestCase):
    def test_fetch_all_scrapers(self):
        scrapers = get_scraper_classes(
            disabled_scrapers=[]
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(issubclass(scraper, ScraperBase))

    def test_fetch_extractors(self):
        scrapers = get_scraper_classes(
            disabled_scrapers=[],
            type_specific=ScraperType.EXTRACTOR
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(issubclass(scraper, ExtractorBase))

    def test_fetch_crawlers(self):
        scrapers = get_scraper_classes(
            disabled_scrapers=[],
            type_specific=ScraperType.CRAWLER
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(issubclass(scraper, CrawlerBase))

    def test_fetch_with_disable(self):
        to_disable = ["mega", "bunkr", "voe"]
        scrapers = get_scraper_classes(
            disabled_scrapers=to_disable
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(scraper.CODENAME not in to_disable)

    def test_fetch_with_enabled_only(self):
        to_enable = ["mega", "bunkr"]
        scrapers = get_scraper_classes(
            enabled_scrapers=to_enable
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(scraper.CODENAME in to_enable)

    def test_fetch_with_enabled_disable(self):
        to_enable = ["mega", "bunkr"]
        to_disable = ["voe"]
        scrapers = get_scraper_classes(
            enabled_scrapers=to_enable,
            disabled_scrapers=to_disable
        )
        for scraper in scrapers:
            with self.subTest(scraper=scraper):
                self.assertTrue(
                    scraper.CODENAME in to_enable,
                    f"{scraper.__name__} with codename '{scraper.CODENAME}' wasn't supposed to be enabled."
                )
                self.assertTrue(
                    scraper.CODENAME not in to_disable,
                    f"{scraper.__name__} with codename '{scraper.CODENAME}' was supposed to be disabled."
                )
