import argparse
from version import __version__
from supported_sites import get_supported_sites

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
