import argparse
import dataclasses

from typing import Union
from version import __version__
from pathlib import Path
from console import console
from supported_sites import print_supported_sites


def make_parser(parser=argparse.ArgumentParser()) -> argparse.ArgumentParser:
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
    parser.add_argument(
        '-s', '--separate-content',
        dest='separate',
        action="store_true",
        help="Provided the flag, downloaded items will NOT be separated into "
             "corresponding folders. (default=True)"
    )
    parser.add_argument(
        '-u', '--save-urls',
        dest='save_urls',
        action="store_true",
        help="Provided the flag, all direct urls for content will be saved into txt"
             "file in the output folder. (default=False)"
    )
    parser.add_argument(
        '--session',
        dest='session',
        help="Path to a last terminated session file. (.json)"
    )
    parser.add_argument(
        '--version',
        action='version',
        version=__version__,
        help='Print program version and exit'
    )
    parser.add_argument(
        '--supported-sites',
        action='store_true',
        dest='supported_sites',
        help='Print supported sites and exit'
    )
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        dest='skip_existing',
        help='Skips items with colliding names.'
             'By default the duplicate items are downloaded with integer added to the name.'
    )
    parser.add_argument(
        '--overwrite-existing',
        action='store_true',
        dest='overwrite_existing',
        help='Ovewrites items with duplicate names.'
             'By default differentiates items by appending integer to the filename.'
    )
    parser.add_argument(
        '--download-path',
        dest='download_path',
        help='Provide custom download path.'
    )
    parser.add_argument(
        '--album-name',
        dest='album_name',
        help='Provide custom album name.'
    )
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Enable debug mode.'
    )
    parser.add_argument(
        '--page-limit',
        dest='crawl_page_limit',
        help='Limit number of pages scraped when crawling.'
    )
    parser.add_argument(
        '--omit-download',
        action='store_true',
        dest='omit_download',
        help="Skip downloading files, useful when just scraping "
             "links like mega.nz or when debugging and don't want to download."
    )
    parser.add_argument(
        '--only-mega',
        action='store_true',
        dest='only_mega',
        help="Only extract mega.nz urls."
    )
    return parser


@dataclasses.dataclass
class Settings:
    input_url: str
    batchfile: Union[Path, None]
    debug: bool
    separate_content: bool
    save_urls: bool
    skip_existing: bool
    overwrite_existing: bool
    download_path: Union[Path, None]
    album_name: Union[str, None]
    crawl_page_limit: Union[int]
    omit_download: bool
    only_mega: bool


def parse_settings() -> Settings:
    args = make_parser().parse_args()

    if args.supported_sites:
        print_supported_sites(console=console)
        exit()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None

    if not (input_url or batchfile):
        input_url = console.input("Enter URL to scrape: ").strip()

    return Settings(
        input_url=input_url,
        batchfile=batchfile,
        separate_content=False if args.separate else True,
        save_urls=args.save_urls,
        skip_existing=args.skip_existing,
        overwrite_existing=args.overwrite_existing,
        download_path=Path(args.download_path) if args.download_path else None,
        album_name=args.album_name,
        debug=args.debug,
        crawl_page_limit=int(args.crawl_page_limit) if args.crawl_page_limit else 0,
        omit_download=args.omit_download,
        only_mega=args.only_mega
    )
