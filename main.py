import requests
from options import parser
from pathlib import Path
from downloader.downloader import Downloader
from utils import load_file, cls, print_data, dump_curr_session
from downloader.downloader import Item
from typing import List
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
                 **kwargs
                 ):
        self.input_link = link
        self.load_from_file = load_from_file
        self.session = requests.Session()
        self.downloader = Downloader(self.session)
        self.options = kwargs

    def main(self):
        if self.input_link:
            self.scrape(self.input_link)
        elif self.load_from_file:
            urls = load_file(self.load_from_file)
            for url in urls:
                self.scrape(url)

    def scrape(self, url):
        """Function that scraper a single link."""
        for scraper_ in get_scraper_classes():
            if scraper_.is_suitable(url):
                print(f"Chosen scraper: {scraper_.DESC}")
                if scraper_.SCRAPER_TYPE == "EXTRACTOR":
                    self.extractor_method(url, scraper_)
                elif scraper_.SCRAPER_TYPE == "CRAWLER":
                    self.crawler_method(url, scraper_)
                return

    def extractor_method(self, url, extractor):
        e = extractor(self.downloader)
        data = e.extract_data(url)
        output_dir_name = input("Enter name for output directory: ")

        self.download(items=data, dir_name=output_dir_name)

    def crawler_method(self, url, crawler, scrape_extracted_links: bool = True):
        c = crawler(self.downloader)

        crawled_html = c.extract_data(url)

        model_name = c.MODEL_NAME
        data = []

        for scraper_ in get_scraper_classes():
            if scraper_.SCRAPER_TYPE == "EXTRACTOR":
                links = []
                for url, html in crawled_html.items():
                    scraper_output = scraper_._extract_from_html(html)
                    if scraper_output:
                        links.extend(scraper_output)
                if links:
                    logging.debug(f"{scraper_.__name__} extracted {len(links)} urls."
                                  f"DATA: {links}")

                    if scrape_extracted_links:
                        s = scraper_(self.downloader)
                        for link_ in links:
                            data.extend(s.extract_data(link_))

        logging.debug(f"Scraped total of {len(data)} items.")
        self.download(items=data, dir_name=model_name)

    def download(self, items: List[Item], dir_name: str):
        while items:
            item = items.pop(0)
            cls()
            print(f"Remaining {len(items)} items.")

            try:
                self.downloader.download_item(
                    item=item,
                    separate_content=self.options["separate"],
                    save_urls=self.options["save_urls"],
                    album_name=dir_name
                )
            except Exception as e:
                print(e)
                print(item)
                dump_curr_session(
                    cookies=dict(self.session.cookies),
                    items_to_download=items
                )
                exit()
            except KeyboardInterrupt:
                dump_curr_session(
                    cookies=dict(self.session.cookies),
                    items_to_download=items
                )
                exit()


if __name__ == '__main__':

    args = parser.parse_args()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None
    separate_content = False if args.separate else True
    save_urls = args.save_urls

    if not (input_url or batchfile):
        raise Exception("You need to provide some URL!")

    logging.basicConfig(
        filename='lols.log',
        level=logging.DEBUG,
        format='%(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S',
        filemode='w'
    )

    lols = LoLs(
        link=input_url,
        load_from_file=batchfile,
        separate=separate_content,
        save_urls=save_urls
    )
    lols.main()
