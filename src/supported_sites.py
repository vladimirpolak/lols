from .scrapers import get_scraper_classes
from rich.console import Console
from pathlib import Path

filename = "supported_sites.txt"


def get_supported_sites(scraper_classes: list = get_scraper_classes()) -> list:
    all_sites = []
    for scraper in scraper_classes:
        domain = scraper.DOMAIN
        description = scraper.DESC.title()
        url = "example url undefined"
        if scraper.SAMPLE_URLS:
            url = scraper.SAMPLE_URLS[0]

        site = f"{description}\n" \
               f"--domain: {domain}\n" \
               f"--example url: {url}\n"
        all_sites.append(site)
    return all_sites


def dump_to_file(data: str, filename: str):
    path = Path().cwd() / filename
    with path.open("w") as file:
        file.write(data)


def print_supported_sites(console: Console, data: list = None):
    if not data:
        data = get_supported_sites(
            scraper_classes=get_scraper_classes()
        )
    for item in data:
        console.print(item)
        console.rule()


if __name__ == '__main__':
    data = get_supported_sites(scraper_classes=get_scraper_classes())
    dump_to_file(
        data="\n".join(data),
        filename=filename
    )
