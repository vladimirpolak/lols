import requests
from options import parser
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
            pass

    def scrape(self, url):
        """Function that scraper a single link."""

        for scraper_ in get_scraper_classes():
            if scraper_.is_suitable(url) and scraper_.SCRAPER_TYPE == "EXTRACTOR":
                print(scraper_.DESC)
                s = scraper_(self.downloader)
                data = s.extract_data(url)

                # Download 'data'
                for item in data:
                    self.downloader.download_item(
                        item=item,
                        separate_content=self.options["separate"],
                        save_urls=self.options["save_urls"]
                    )

            elif scraper_.is_suitable(url) and scraper_.SCRAPER_TYPE == "CRAWLER":
                self.use_crawler(url, scraper_, scrape_links_found=True)
            # else:
            #     raise ExtractionError("FOUND NO MATCHING EXTRACTOR.")

    def use_crawler(self, url, crawler, scrape_links_found: bool = False):
        print(crawler.DESC)

        c = crawler(self.downloader)
        html = c.extract_data(url)
        data = []

        for scraper_ in get_scraper_classes():
            if scraper_.SCRAPER_TYPE == "EXTRACTOR":

                # print(scraper_.DESC)
                try:
                    links = scraper_._extract_from_html(html)
                except Exception as e:
                    raise ExtractionError(f"{e}\nError extracting links with {scraper_}.")
                if links:
                    logging.debug(f"{scraper_.__name__} extracted {len(links)} urls. DATA: {links}")

                    if scrape_links_found:
                        s = scraper_(self.downloader)
                        for link_ in links:
                            try:
                                data.extend(s.extract_data(link_))
                            except Exception as e:
                                raise ExtractionError(f"{e}\n{scraper_}\nError extracting data from link: {link_}")

        logging.debug(f"Scraped total of {len(data)} items.")

        # Download 'data'
        for item in data:
            self.downloader.download_item(
                item=item,
                separate_content=self.options["separate"],
                save_urls=self.options["save_urls"]
            )


if __name__ == '__main__':

    args = parser.parse_args()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None
    separate_content = False if args.separate else True
    save_urls = args.save_urls

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
    # options = {}
    # if input_url:
    #     options.update({
    #         "link": input_url
    #     })

    lols = LoLs(
        link=input_url,
        load_from_file=batchfile,
        separate=separate_content,
        save_urls=save_urls
    )
    lols.main()
