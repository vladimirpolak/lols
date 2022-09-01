import argparse
from .version import __version__
from pathlib import Path
from .console import console
from .supported_sites import print_supported_sites

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
parser.add_argument(
    '-s', '--separate-content',
    dest='separate',
    action="store_true",
    help="Provided the flag, downloaded items will be separated into"
         "corresponding folders by the content type. (default=True)"
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


def parse_options():
    args = parser.parse_args()

    input_url = args.url
    batchfile = Path(args.batchfile) if args.batchfile else None
    separate_content = False if args.separate else True
    save_urls = args.save_urls
    ss = args.supported_sites
    if ss:
        print_supported_sites(console=console)
        exit()

    if not (input_url or batchfile):
        console.print("[bright_red]You need to provide some URL![/bright_red]")
        exit()

    app_options = {
        "link": input_url,
        "load_from_file": batchfile,
        "separate": separate_content,
        "save_urls": save_urls
    }
    return app_options


