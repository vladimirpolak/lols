import unittest
from lols.scrapers import get_scraper_classes, ScraperType
import time
from lols import LolsClient


class ScrapingTest(unittest.TestCase):
    def test_extractors_scraping(self):
        with LolsClient() as client:
            for extractor in get_scraper_classes(type_specific=ScraperType.EXTRACTOR):
                for url, results in extractor.TESTS.items():
                    with self.subTest(url=url, results=results):
                        scraped_items = client.scrape(url)

                        if results.get("urls_may_differ", None):
                            scraped_items = {
                                (item.filename, item.extension, item.content_type.value)
                                for item
                                in scraped_items
                            }
                            expected_items = {
                                (item["filename"], item["extension"], item["content_type"])
                                for item
                                in results["items"]
                            }
                        else:
                            scraped_items = {
                                (item.source, item.filename, item.extension, item.content_type.value)
                                for item
                                in scraped_items
                            }
                            expected_items = {
                                (item["source"], item["filename"], item["extension"], item["content_type"])
                                for item
                                in results["items"]
                            }
                        self.assertSetEqual(scraped_items, expected_items)
                        time.sleep(0.5)