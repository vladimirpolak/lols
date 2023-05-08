from lols.scrapers import get_scraper_classes
from lols.utils import get_supported_sites
from pathlib import Path

docs_folder = "docs"
filename = "supported_sites.txt"


def dump_to_file(data: str, filepath: Path):
    with filepath.open("w") as file:
        file.write(data)



if __name__ == '__main__':
    data = get_supported_sites(scraper_classes=get_scraper_classes())

    docs = Path().cwd().parent / docs_folder
    if not docs.exists():
        docs.mkdir()

    path = docs / filename

    dump_to_file(
        data="\n".join(data),
        filepath=path
    )
