from .settings import (make_parser,
                       get_disabled_scrapers_from_args,
                       get_selected_extractors_from_args,
                       get_skip_content_type_args)
from .http import (Item,
                   ContentType,
                   download_item)
from .path_creator import PathCreator
from .scrapers import (get_scraper_classes,
                       ScraperType,
                       ExtractorBase,
                       CrawlerBase)
from .utils import (logs_setup,
                    load_file,
                    get_supported_sites,
                    save_to_file)
from .exceptions import PasswordRequired

from typing import List, Type, Union, Dict
from pathlib import Path
from collections import defaultdict
import requests
import logging
import pprint


class LolsClient:
    """
    LolsClient is a client class for managing and executing scraping of variety hosting sites using
    multitude of scrapers also supporting download.
    """
    session: requests.Session

    def __init__(
            self,
            session: requests.Session = None,
            scrapers_to_disable: List[str] = None,
            enabled_extractors: List[str] = None,
            crawler_page_limit: int = None):
        """

        :param session: requests.Session - Option to provide custom Session object
        :param scrapers_to_disable: List[str] - Optional list,
                                                containing string codenames of extractors to be disabled.
        :param enabled_extractors: List[str] - Optional list,
                                                containing string codenames of the only extractors that are to be used.
        :param crawler_page_limit: int - Limit number of pages crawled when scraping forum threads.
        """

        self.session = session or requests.Session()
        self._scrapers_to_disable = scrapers_to_disable or []
        self._enabled_extractors = enabled_extractors or []
        self.crawler_page_limit = crawler_page_limit or 0

        self.thread_name = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    @property
    def all_scrapers(self):
        return get_scraper_classes()

    @property
    def extractors(self) -> List[Type[ExtractorBase]]:
        return get_scraper_classes(type_specific=ScraperType.EXTRACTOR,
                                   disabled_scrapers=self._scrapers_to_disable,
                                   enabled_scrapers=self._enabled_extractors)

    @property
    def crawlers(self) -> List[Type[CrawlerBase]]:
        return get_scraper_classes(type_specific=ScraperType.CRAWLER,
                                   disabled_scrapers=self._scrapers_to_disable,
                                   enabled_scrapers=self._enabled_extractors)

    def _assign_scraper(self, url: str) -> Union[Type[ExtractorBase], Type[CrawlerBase], None]:
        """Function that picks the scraper that is capable of extracting from the given url."""
        for s in self.all_scrapers:
            if s.is_suitable(url):
                return s
        return None

    def extractor_method(self,
                         url: str,
                         extractor: Type[ExtractorBase],
                         session: requests.Session = None):
        return extractor(session or self.session).extract_data(url)

    def crawler_method(self,
                       url: str,
                       crawler: Type[CrawlerBase],
                       session: requests.Session = None) -> List[Item]:
        """
        Scraping method used for the likes of forums where multitude of different hosting sites can be found.
        First the Thread html is scraped and then each of extractors extracts urls from the given html.
        If an extractor finds url it can work with, it then scrapes the content from the given url.

        :param url:
        :param crawler:
        :param session:
        :return:
        """
        crawler = crawler(
            session or self.session,
            page_limit=self.crawler_page_limit
        )

        # Crawl the target thread for html
        crawled_html = crawler.extract_data(url)

        # Thread name (Used to name an output directory)
        self.thread_name = crawler.THREAD_NAME

        # Run the scraped html against extractors
        data = []
        logging.info("Scraping data from extracted URLs...")
        for extractor in self.extractors:

            # Loops through crawled pages and extract known URLs
            links = dict()
            for url, html in crawled_html.items():
                extracted_urls = extractor.extract_from_html(url, html)
                if extracted_urls:
                    links[url] = extracted_urls

            # If any valid links were scraped here we extract data from them
            if links:
                e = extractor(session or self.session)
                for origin_url, urls in links.items():
                    for url in urls:
                        try:
                            scraped_data = e.extract_data(url)
                        except PasswordRequired:
                            logging.error(
                                f"Password Protected URL: '{url}', OriginUrl: {origin_url}"
                            )
                        else:
                            data.extend(scraped_data)
        return data

    def scrape(self, url, session: requests = None) -> List[Item]:
        assigned_scraper = self._assign_scraper(url)
        if not assigned_scraper:
            logging.info(f"No scraper matched url: {url}")
            return []

        if issubclass(assigned_scraper, ExtractorBase):
            return self.extractor_method(url, assigned_scraper, session)
        if issubclass(assigned_scraper, CrawlerBase):
            return self.crawler_method(url, assigned_scraper, session)

    def download(self,
                 items: List[Item],
                 output_dir: Union[str, Path],
                 session: requests.Session = None,
                 separate_content: bool = False,
                 skip_existing: bool = False,
                 overwrite_existing: bool = False,
                 skip_content_type: List[ContentType] = None,
                 verbose: bool = False,
                 ):
        """
        Download scraped items.

        :param items: List[Item] - List of 'Item' items to be downloaded
        :param output_dir: str | Path - Output directory
        :param session: requests.Session - Option to provide custom Session object
        :param separate_content: bool - If True downloaded items are separated into folders based on content type. Default False
        :param skip_existing: bool - If True files with colliding filenames will be skipped, otherwise an integer is added to a duplicate filename. Default False
        :param overwrite_existing: bool - If True files with coliding filenames will be overwritten rather than renamed, Default False
        :param skip_content_type: List[ContentType] - Optional list of 'ContentType' enums that are to be skipped.
        :param verbose: bool - Verbose download progress to console. Default False
        """
        pass
        items = items
        session = session or self.session
        skip_content_type = skip_content_type or []

        while items:
            item = items.pop(0)

            download_path = PathCreator.generate_download_path(
                album_folder=output_dir,
                download_item=item,
                skip_existing=skip_existing,
                overwrite_existing=overwrite_existing,
                separate_content=separate_content
            )

            if download_path:
                if item.content_type not in skip_content_type:
                    download_item(item, download_path, session, verbose)


def main():
    parser = make_parser()
    args = parser.parse_args()

    logs_setup(debug=args.debug)

    album_name = args.album_name
    url = args.url
    batch = args.batchfile

    # Print out supported sites and exit
    if args.supported_sites:
        print("\n\n".join(get_supported_sites(get_scraper_classes())))

    # Neither URL or Batch files were provided
    elif not (url or batch):
        print("You need to provide URL or batch file containing URL/s!")

    else:
        # Initiate client based on input args
        client = LolsClient(
            scrapers_to_disable=get_disabled_scrapers_from_args(args),
            enabled_extractors=get_selected_extractors_from_args(args),
            crawler_page_limit=args.crawl_page_limit
        )

        # Set output folder
        download_path = args.download_path
        if download_path:
            output_folder = Path(download_path) / album_name
        else:
            output_folder = Path().cwd() / album_name

        # Scrape URL | Batch File
        if url:
            items = client.scrape(url=url)
        elif batch:
            items = []
            for url in load_file(Path(batch)):
                items.extend(client.scrape(url))

        # Developer's test, scrapes items and prints them out to console, no download
        if args.test:
            results = dict()
            results["items"] = [item.to_dict() for item in items]

            content_count: Dict[ContentType, int] = defaultdict(int)
            for item in items:
                content_count[item.content_type] += 1

            pprint.pprint(results)
            for content_type, count in content_count.items():
                print(f"{content_type.value.title()}s scraped: {count}")

        else:
            # Save scraped items URLs to .txt file
            for item in items:
                if (args.save_urls
                        or item.content_type == ContentType.URL):
                    save_to_file(
                        file=output_folder / "urls.txt",
                        data=item.source
                    )

            # Download scraped items
            if not args.omit_download:
                client.download(
                    items=items,
                    separate_content=args.separate_content,
                    skip_existing=args.skip_existing,
                    overwrite_existing=args.overwrite_existing,
                    output_dir=args.album_name,
                    skip_content_type=get_skip_content_type_args(args),
                    verbose=True
                )

