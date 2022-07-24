from scrapers import get_scraper_classes


class UrlMatchingTest:
    @classmethod
    def test(cls):
        scraper_classes = get_scraper_classes()
        for scraper in scraper_classes:
            for url in scraper.SAMPLE_URLS:
                if not scraper.is_suitable(url):
                    print(f"{scraper.__name__} FAILED TO MATCH: {url}")


if __name__ == '__main__':
    UrlMatchingTest.test()
