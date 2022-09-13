from ._all import *

_ALL_SCRAPERS = [
    klass
    for name, klass in globals().items()
    if (name.endswith('Extractor')
        or name.endswith('Crawler'))
]
_ALL_EXTRACTORS = [
    klass
    for name, klass in globals().items()
    if name.endswith('Extractor')
]
_ALL_CRAWLERS = [
    klass
    for name, klass in globals().items()
    if name.endswith('Crawler')
]


def get_scraper_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_SCRAPERS


def get_extractor_classes():
    return _ALL_EXTRACTORS


def get_crawler_classes():
    return _ALL_CRAWLERS
