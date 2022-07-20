from scrapers import get_scraper_classes

# Test Url Matching
scraper_classes = get_scraper_classes()
for s in scraper_classes:
    print(f"\n{s.__name__}")
    for url in s.SAMPLE_URLS:
        print(s.is_suitable(url))
