from .scrapers import get_codenames
from .version import __version__
from .http import ContentType

from typing import List
import argparse


def inject_args_disabled_scrapers(parser: argparse.ArgumentParser):
    """
    Add arguments for disabling scrapers.

    :param parser: argparse.ArgumentParser
    :return:
    """
    scraper_group = parser.add_argument_group('Disable Scraper')
    for name in get_codenames():
        scraper_group.add_argument(
            f'--d-{name}',
            dest=f'd_{name}',
            action='store_true',
            help=f"Disable {name.title()}"
        )


def get_disabled_scrapers_from_args(args: argparse.Namespace) -> List[str]:
    """Fetch list of disabled scrapers from input args."""
    return [codename for codename in get_codenames() if args.__dict__.pop(f"d_{codename}", False)]


def inject_args_selected_extractors(parser: argparse.ArgumentParser):
    """
    Add arguments for specifying extractors to use.

    :param parser: argparse.ArgumentParser
    :return:
    """
    scraper_group = parser.add_argument_group('Specify Extractors to use')
    for name in get_codenames():
        scraper_group.add_argument(
            f'--o-{name}',
            dest=f'o_{name}',
            action='store_true',
            help=f"Select {name.title()} for use."
        )


def get_selected_extractors_from_args(args: argparse.Namespace) -> List[str]:
    """Fetch list of selected scrapers from input args."""
    return [codename for codename in get_codenames() if args.__dict__.pop(f"o_{codename}", False)]


def get_skip_content_type_args(args: argparse.Namespace) -> List[ContentType]:
    output = []
    if args.__dict__.pop("skip_vid", False):
        output.append(ContentType.VIDEO)
    if args.__dict__.pop("skip_img", False):
        output.append(ContentType.IMAGE)
    if args.__dict__.pop("skip_audio", False):
        output.append(ContentType.AUDIO)
    if args.__dict__.pop("skip_archive", False):
        output.append(ContentType.ARCHIVE)
    return output


def inject_args_download(parser: argparse.ArgumentParser):
    download_group = parser.add_argument_group('Download Options')
    download_group.add_argument(
        '--omit-download',
        action='store_true',
        dest='omit_download',
        help="Skip downloading files, useful when just scraping "
             "links like mega.nz or when debugging and don't want to download."
    )
    # download_group.add_argument(
    #     '--album-name',
    #     dest='album_name',
    #     help='Provide custom album name.'
    # )
    download_group.add_argument(
        '--skip-existing',
        action='store_true',
        dest='skip_existing',
        help='Skips items with colliding names.'
             'By default the duplicate items are downloaded with integer added to the name.'
    )
    download_group.add_argument(
        '--overwrite-existing',
        action='store_true',
        dest='overwrite_existing',
        help='Ovewrites items with duplicate names.'
             'By default differentiates items by appending integer to the filename.'
    )
    download_group.add_argument(
        '--download-path',
        dest='download_path',
        help='Provide custom download path.'
    )
    download_group.add_argument(
        '-s', '--separate-content',
        dest='separate_content',
        action="store_true",
        help="Provided the flag, downloaded items will be separated into "
             "corresponding folders."
    )
    download_group.add_argument(
        '--skip-vid',
        dest='skip_vid',
        action="store_true",
        help="Skip download of videos."
    )
    download_group.add_argument(
        '--skip-img',
        dest='skip_img',
        action="store_true",
        help="Skip download of images."
    )
    download_group.add_argument(
        '--skip-audio',
        dest='skip_audio',
        action="store_true",
        help="Skip download of audio tracks."
    )
    download_group.add_argument(
        '--skip-archive',
        dest='skip_archive',
        action="store_true",
        help="Skip download of archives."
    )

def inject_args_testing(parser: argparse.ArgumentParser):
    test_group = parser.add_argument_group('Test Options')
    test_group.add_argument(
        '--test',
        action='store_true',
        dest='test',
        help="Run as a test, outputs the scraped items to stdout as dictionary."
    )


def make_parser(parser=argparse.ArgumentParser()) -> argparse.ArgumentParser:
    parser.add_argument(
        "album_name",
        help="Name of the outpuf folder.",
        type=str
    )
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
        '-u', '--save-urls',
        dest='save_urls',
        action="store_true",
        help="Provided the flag, all direct urls for content will be saved into txt"
             "file in the output folder. (default=False)"
    )
    # parser.add_argument(
    #     '--session',
    #     dest='session',
    #     help="Path to a last terminated session file. (.json)"
    # )
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
        help='Show supported sites.'
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
        type=int,
        help='Limit number of pages scraped when crawling.'
    )
    inject_args_download(parser)
    inject_args_disabled_scrapers(parser)
    inject_args_selected_extractors(parser)
    inject_args_testing(parser)
    return parser
