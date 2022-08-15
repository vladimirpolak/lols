import requests
from options import parser
from pathlib import Path
from downloader import Downloader
from scrapers._scraper_base import ExtractorBase, CrawlerBase, ScraperBase
from utils import load_file, clear_output, print_data, dump_curr_session
from downloader.models import Item
from typing import Union, List, TypeVar
import logging
from scrapers import get_scraper_classes

# logging.debug('This message should go to the log file')
# logging.info('So should this')
# logging.warning('And this, too')
# logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

Extractor = TypeVar('Extractor', bound='ExtractorBase')
Crawler = TypeVar('Crawler', bound='CrawlerBase')


class LoLs:
    def __init__(self,
                 link: str = None,
                 load_from_file: str = None,
                 **kwargs
                 ):
        self.input_link = link
        self.load_from_file = load_from_file
        self.session = kwargs.pop("session", None) or requests.Session()
        self.downloader = kwargs.pop("downloader", None) or Downloader(self.session)
        self.options = kwargs

    def main(self):
        """
        Picks the logic based on the user input either a single url or a text file containing multiple urls.
        """
        if self.input_link:
            self.scrape(self.input_link)

        elif self.load_from_file:
            urls = load_file(self.load_from_file)
            for url in urls:
                self.scrape(url)

    def scrape(self, url: str):
        """
        Urls that lead to either a single item or album of items on one site is handled by Extractor type of scraper.
        Urls that lead to a thread/album that can contain multiple of items and external urls
        is handled by Crawler type of scraper.

        Crawler scrapes the HTML of the thread (usually spanning through multiple pages) that is then run against
        Extractors that extract their type of url from the html if it contains any, then they extract the content
        from the extracted urls.

        :param url: str
        """
        scraper = self._assign_scraper(url)

        if not scraper:
            return

        print(f"Chosen scraper: {scraper.DESC}")
        if issubclass(scraper, ExtractorBase):
            self.extractor_method(url, scraper)
        elif issubclass(scraper, CrawlerBase):
            self.crawler_method(url, scraper)

    @staticmethod
    def _assign_scraper(url: str) -> Union[ExtractorBase, CrawlerBase]:
        """Function that picks the scraper that is capable of extracting from the given url."""
        for s in get_scraper_classes():
            if s.is_suitable(url):
                return s

    def extractor_method(self,
                         url: str,
                         extractor: Extractor):
        # Initiate extractor
        e = extractor(self.downloader)

        # Extract data
        data = e.extract_data(url)

        # Displays the amount/type of scraped data
        print_data(data)

        if data:
            output_dir_name = input("Enter name for output directory: ")
            self.download(items=data, dir_name=output_dir_name)

    def crawler_method(self,
                       url: str,
                       crawler: Crawler,
                       scrape_extracted_links: bool = True):
        # Initiate crawler
        c = crawler(self.downloader)

        # Crawl the target thread for html
        crawled_html = c.extract_data(url)

        # Thread name (Used to name an output directory)
        model_name = c.THREAD_NAME

        # Run the crawled html against Extractor classes
        data = []
        for scraper in get_scraper_classes():
            if scraper.SCRAPER_TYPE == "EXTRACTOR":
                links = []

                # Loops through crawled pages
                for url, html in crawled_html.items():
                    # Searches for valid urls here
                    scraper_output = scraper.extract_from_html(html)
                    if scraper_output:
                        links.extend(scraper_output)

                # If any valid links were scraped it extracts data from them
                if links:
                    logging.debug(f"{scraper.__name__} extracted {len(links)} urls."
                                  f"DATA: {links}")
                    if scrape_extracted_links:
                        s = scraper(self.downloader)
                        for link_ in links:
                            data.extend(s.extract_data(link_))

        # Displays the amount/type of scraped data
        logging.debug(f"Scraped total of {len(data)} items.")

        print_data(data)
        if data:
            self.download(items=data, dir_name=model_name)

    def download(self, items: List[Item], dir_name: str):
        while items:
            print(f"Remaining {len(items)} items.")
            item = items.pop(0)

            try:
                self.downloader.download_item(
                    item=item,
                    separate_content=self.options["separate"],
                    save_urls=self.options["save_urls"],
                    album_name=dir_name
                )
                if items:
                    clear_output(lines_to_clear=4)
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
        print(f"\nOutput directory: {dir_name}")


if __name__ == '__main__':

    args = parser.parse_args()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None
    separate_content = False if args.separate else True
    save_urls = args.save_urls

    if not (input_url or batchfile):
        raise Exception("You need to provide some URL!")

    logging.basicConfig(
        handlers=[logging.FileHandler('lols.log', 'w', 'utf-8')],
        level=logging.DEBUG,
        format='%(levelname)s %(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S',
    )

    lols = LoLs(
        link=input_url,
        load_from_file=batchfile,
        separate=separate_content,
        save_urls=save_urls
    )
    lols.main()
