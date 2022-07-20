from scrapers import get_scraper_classes


class UrlMatchingTest:
    @classmethod
    def test(cls):
        scraper_classes = get_scraper_classes()
        for s in scraper_classes:
            print(f"\n{s.__name__}")
            for url in s.SAMPLE_URLS:
                if not s.is_suitable(url):
                    print(f"FAILED TO MATCH: {url}")
