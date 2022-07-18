import requests
import argparse
from pathlib import Path
from downloader.downloader import Downloader
from exceptions import ExtractionError
import logging
from scrapers import get_scraper_classes

# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')
# logging.error('And non-ASCII stuff, too, like Øresund and Malmö')


class LoLs:
    def __init__(self,
                 link: str = None,
                 load_from_file: str = None,
                 debug=False
                 ):
        self.input_link = link
        self.load_from_file = load_from_file
        self.session = requests.Session()
        self.downloader = Downloader()
        self.downloader.set_session(self.session)

    def main(self):
        if self.input_link:
            self.scrape(self.input_link)
        elif self.load_from_file:
            pass

    def scrape(self, url):
        """Function that scraper a single link."""

        for scraper_ in get_scraper_classes():
            if scraper_.is_suitable(url) and scraper_.SCRAPER_TYPE == "EXTRACTOR":
                print(scraper_.DESC)
                s = scraper_(self.downloader)
                data = s.extract_data(url)
                print(data)

                # Download 'data'

            elif scraper_.is_suitable(url) and scraper_.SCRAPER_TYPE == "CRAWLER":
                self.scrape_thread(url, scraper_)
            # else:
            #     raise ExtractionError("FOUND NO MATCHING EXTRACTOR.")

    def scrape_thread(self, url, scraper):
        print(scraper.DESC)

        s = scraper()
        s.set_downloader(self.downloader)
        html = s.extract_data(url)
        all_items = []

        for scraper_ in get_scraper_classes():
            if scraper_.SCRAPER_TYPE == "EXTRACTOR":

                # print(scraper_.DESC)
                try:
                    links = scraper_._extract_from_html(html)
                except Exception as e:
                    raise ExtractionError(f"{e}\nError extracting links with {scraper_}.")
                if links:
                    s = scraper_()
                    s.set_downloader(self.downloader)
                    for link_ in links:
                        try:
                            all_items.extend(s.extract_data(link_))
                        except Exception as e:
                            raise ExtractionError(f"{e}\n{scraper_}\nError extracting data from link: {link_}")

        # download all_items[Item]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        help="URL to scrape.",
        nargs='?',
        type=str
    )
    parser.add_argument(
        '-a', '--batch-file',
        dest='batchfile', metavar='FILE',
        help="File containing URLs to download ('-' for stdin), one URL per line. "
             "Lines starting with '#', ';' or ']' are considered as comments and ignored."
    )
    args = parser.parse_args()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None

    if not (input_url or batchfile):
        raise Exception("You need to provide some URL!")

    # Check if path to file is absolute
    # batchfile.is_absolute()

    logging.basicConfig(
        filename='lols.log',
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S',
        filemode='w'
    )
    options = {}
    if input_url:
        options.update({
            "link": input_url
        })

    lols = LoLs(**options)
    lols.main()
