from ._all import *

_ALL_CLASSES = [
    klass
    for name, klass in globals().items()
    if (name.endswith('Extractor')   # and name != 'GenericIE'
        or name.endswith('Crawler'))
]


def get_scraper_classes():
    """ Return a list of supported extractors.
    The order does matter; the first extractor matched is the one handling the URL.
    """
    return _ALL_CLASSES
