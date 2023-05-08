from lols.scrapers import get_scraper_classes
from lols.utils import get_supported_sites
from rich.console import Console
from pathlib import Path

docs_folder = "docs"
filename = "supported_sites.txt"


def dump_to_file(data: str, filepath: Path):
    with filepath.open("w") as file:
        file.write(data)


# def print_supported_sites(console: Console, data: list = None):
#     if not data:
#         data = get_supported_sites(
#             scraper_classes=get_scraper_classes()
#         )
#     for item in data:
#         console.print(item)
#         console.rule()


if __name__ == '__main__':
    data = get_supported_sites(scraper_classes=get_scraper_classes())

    docs = Path().cwd() / docs_folder
    if not docs.exists():
        docs.mkdir()

    path = docs / filename

    dump_to_file(
        data="\n".join(data),
        filepath=path
    )
