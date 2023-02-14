import requests
from console import console
from downloader import Downloader
from scrapers._scraper_base import ExtractorBase, CrawlerBase
from utils import load_file, print_data, dump_curr_session, logs_setup
from downloader.models import Item
from typing import Union, List, TypeVar
import logging
from settings import Settings, parse_settings
from scrapers import get_scraper_classes, get_extractor_classes


Extractor = TypeVar('Extractor', bound='ExtractorBase')
Crawler = TypeVar('Crawler', bound='CrawlerBase')


class LoLs:
    def __init__(self, settings: Settings):
        self.settings = settings

        self.input_link = self.settings.input_url
        self.batchfile = self.settings.batchfile
        self.session = requests.Session()
        self.downloader = Downloader(self.session, self.settings.download_path)

        self.thread_name = ""

    def main(self):
        """
        Picks the logic based on the user input either a single url or a text file containing multiple urls.
        """
        if self.input_link:
            self.scrape(self.input_link)

        elif self.batchfile:
            urls = load_file(self.batchfile)
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
            console.print(f"No valid scraper for: {url}.")
            return

        console.print(f"Chosen scraper: [green]{scraper.DESC}[/green]")
        if issubclass(scraper, ExtractorBase):
            data: List[Item] = self.extractor_method(url, scraper)
        elif issubclass(scraper, CrawlerBase):
            data: List[Item] = self.crawler_method(url, scraper)

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
        return extractor(self.downloader).extract_data(url)

    def crawler_method(self,
                       url: str,
                       crawler: Crawler,
                       scrape_extracted_links: bool = True) -> List[Item]:
        # Initiate crawler
        c = crawler(self.downloader, page_limit=self.settings.crawl_page_limit)

        # Crawl the target thread for html
        crawled_html: dict = c.extract_data(url)

        # Thread name (Used to name an output directory)
        self.thread_name = c.THREAD_NAME

        # Run the crawled html against Extractor classes
        data = []
        for extractor in get_extractor_classes():
            if settings.only_mega and extractor.DOMAIN != "mega.nz":
                continue
            links = []

            # Loops through crawled pages
            for url, html in crawled_html.items():
                # Searches for valid urls here
                scraper_output = extractor.extract_from_html(url, html)
                if scraper_output:
                    links.extend(scraper_output)

            # If any valid links were scraped it extracts data from them
            if links:
                logging.debug(f"{extractor.__name__} extracted {len(links)} urls."
                              f"DATA: {links}")
                if scrape_extracted_links:
                    s = extractor(self.downloader)
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
                    curr_item_num=step,
                    total_items_len=list_length,
                    album_name=self.settings.album_name or dir_name,
                    separate_content=self.settings.separate_content,
                    save_urls=self.settings.save_urls,
                    skip_existing=self.settings.skip_existing,
                    overwrite_existing=self.settings.overwrite_existing,
                    omit_download=self.settings.omit_download
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
    settings = parse_settings()

    logs_setup(settings.debug)
    lols = LoLs(settings)
    lols.main()
