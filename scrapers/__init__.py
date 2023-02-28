from scrapers import all_scrapers
from scrapers._scraper_base import ScraperType, ScraperBase, ExtractorBase, CrawlerBase
from typing import List
import inspect


def general_conditions_met(scraper_class: ScraperBase) -> bool:
    return all([
        scraper_class.is_active()
    ])


def is_correct_type(scraper_class: ScraperBase, requested_type: ScraperType) -> bool:
    if not requested_type:
        return True
    return scraper_class.SCRAPER_TYPE == requested_type


def is_enabled(scraper_class: ScraperBase, disabled_scrapers: list, enabled_scrapers: list):
    if enabled_scrapers:
        return scraper_class.CODENAME in enabled_scrapers
    if disabled_scrapers:
        return scraper_class.CODENAME not in disabled_scrapers
    return True


def all_conditions_met(obj, disabled_scrapers: list, enabled_scrapers: list, requested_type: ScraperType) -> bool:
    return all([
        general_conditions_met(obj),
        is_enabled(obj, disabled_scrapers, enabled_scrapers),
        is_correct_type(obj, requested_type)
    ])


def get_scraper_classes(disabled_scrapers: list = None,
                        enabled_scrapers: list = None,
                        type_specific: ScraperType = None) -> list:
    """
    Used to fetch list of scraper classes.

    :param disabled_scrapers: list of scraper codenames that are supposed to be disabled.
    :param enabled_scrapers: list of scrapers that are only to be used.
    :param type_specific: optional ScraperType Enum to specify a type of scrapers
    :return: list of scraper classes
    """
    if disabled_scrapers is None:
        disabled_scrapers = []
    if enabled_scrapers is None:
        enabled_scrapers = []
    return [
        obj
        for name, obj
        in inspect.getmembers(all_scrapers, inspect.isclass)
        if all_conditions_met(obj, disabled_scrapers, enabled_scrapers, type_specific)
    ]


def get_crawler_classes():
    return [
        klass
        for name, klass in globals().items()
        if (name.endswith('Crawler')
            and general_conditions_met(klass))
    ]
