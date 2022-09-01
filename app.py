import requests
from console import console
from options import parse_options
from downloader import Downloader
from scrapers._scraper_base import ExtractorBase, CrawlerBase
from utils import load_file, print_data, dump_curr_session
from downloader.models import Item
from typing import Union, List, TypeVar
import logging
from scrapers import get_scraper_classes


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
        self.thread_name = ""
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

        console.print(f"Chosen scraper: [green]{scraper.DESC}[/green]")
        if issubclass(scraper, ExtractorBase):
            data = self.extractor_method(url, scraper)
        elif issubclass(scraper, CrawlerBase):
            data = self.crawler_method(url, scraper)

        # Displays the amount/type of scraped data
        print_data(data)

        if self.thread_name and data:
            self.download(items=data, dir_name=self.thread_name)
        elif data:
            output_dir_name = console.input("Enter name for output directory: ")
            self.download(items=data, dir_name=output_dir_name)

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

        return e.extract_data(url)

    def crawler_method(self,
                       url: str,
                       crawler: Crawler,
                       scrape_extracted_links: bool = True) -> List[Item]:
        # Initiate crawler
        c = crawler(self.downloader)

        # Crawl the target thread for html
        crawled_html = c.extract_data(url)

        # Thread name (Used to name an output directory)
        self.thread_name = c.THREAD_NAME

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
        return data

    def download(self, items: List[Item], dir_name: str):

        list_length = len(items)
        step = 1
        while items:
            item = items.pop(0)

            try:
                self.downloader.download_item(
                    item=item,
                    separate_content=self.options["separate"],
                    save_urls=self.options["save_urls"],
                    album_name=dir_name,
                    curr_item_num=step,
                    total_length=list_length
                )
                step += 1

            except KeyboardInterrupt:
                items.append(item)
                dump_curr_session(
                    cookies=dict(self.session.cookies),
                    items_to_download=items
                )
                exit()
            except Exception as e:
                print(e)
                print(item)
                dump_curr_session(
                    cookies=dict(self.session.cookies),
                    items_to_download=items
                )
                exit()
        console.print(f"\nOutput directory: {dir_name}")


if __name__ == '__main__':
    app_options = parse_options()

    logging.basicConfig(
        handlers=[logging.FileHandler('../last_run.log', 'w', 'utf-8')],
        level=logging.DEBUG,
        format='%(levelname)s %(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S',
    )

    lols = LoLs(**app_options)
    lols.main()
