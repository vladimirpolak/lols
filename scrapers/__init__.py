from ._all import *
from _scraper_base import ScraperType


def general_conditions_met(scraper_class) -> bool:
    return all([
        scraper_class.is_active()
    ])


_ALL_SCRAPERS = [
    klass
    for name, klass in globals().items()
    if ((name.endswith('Extractor')
        or name.endswith('Crawler'))
        and general_conditions_met(klass))
]


def get_scraper_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_SCRAPERS


def get_extractor_classes():
    return [
        klass
        for name, klass in globals().items()
        if (name.endswith('Extractor')
            and general_conditions_met(klass))
    ]


def get_crawler_classes():
    return [
        klass
        for name, klass in globals().items()
        if (name.endswith('Crawler')
            and general_conditions_met(klass))
    ]
