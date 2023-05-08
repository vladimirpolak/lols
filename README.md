<h1 style="text-align: center;">Lols</h1>

<!-- ABOUT THE PROJECT -->
## About

Goal of this project is to have Bulk downloader/Content scraper capable of scraping content
from multiple hosting sites/forums. Simple premise: user inputs a page url and scraper downloads it's contents.

<!-- SUPPORTED SITES -->
## Supported sites
View supported sites and their corresponding codenames [here](docs/supported_sites.txt)

<!-- GETTING STARTED -->
## Getting Started

You can use Lols as either a command line application or
you can incorporate it into your own python scripts as an external library.

### Installation

1. Download and install latest [python](https://www.python.org/downloads/).
2. In command line run:
   ```sh
   pip install lols
   ```

## Usage
### Command Line Application

1. Navigate to the folder where you want scraper to be downloading files.
Bare in mind Lols create separate subfolder for each scrape.

2. Basic usage syntax is as follows:
```sh
lols [output_directory] [url] [options]
```
_Learn all options in Command Line App Options section or with help dialogue:_

```sh
lols --help
```

### Library
You can use Lols in your own custom script and take advantage of all the prewritten extractors.

Once you pip-installed Lols in either global interpreter or the virtual evniroment you set up
you can use the library as follows.

```python
from lols import LolsClient, Item
from typing import List

url = "www.url.you/want-to-scrape"

# Initiate client
client = LolsClient()

# Scrape URL
items: List[Item] = client.scrape(url=url)
```

To disable specific extractor for whatever reason be it buggy servers
or your disinterest initiate the client like so:
```python
client = LolsClient(
   scrapers_to_disable=['bunkr'] # Option accepts list of codenames in string format
)
```

Or you can specify the only Extractor/s to use:
```python
client = LolsClient(
   enabled_extractors=['bunkr'] # Option accepts list of codenames in string format
)
```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Command Line App Options
   ```
usage: lols [-h] [-a FILE] [-u] [--version] [--supported-sites] [-d] [--page-limit CRAWL_PAGE_LIMIT] [--omit-download] [--skip-existing] [--overwrite-existing]
            [--download-path DOWNLOAD_PATH] [-s] [--skip-vid] [--skip-img] [--skip-audio] [--skip-archive] [--d-anon] [--d-bunkr] [--d-cdrop] [--d-erome]
            [--d-forum_lm] [--d-forum_nstar] [--d-forum_ps] [--d-forum_smg] [--d-gofile] [--d-hex] [--d-hload] [--d-ibam] [--d-ibb] [--d-imgbox] [--d-imghaha]
            [--d-imgtwist] [--d-jpgchurch] [--d-lovefap] [--d-mega] [--d-pixl] [--d-pxdrain] [--d-pxhost] [--d-sendvid] [--d-simpcity] [--d-streamlare]
            [--d-streamtape] [--d-voe] [--d-xvids] [--o-anon] [--o-bunkr] [--o-cdrop] [--o-erome] [--o-forum_lm] [--o-forum_nstar] [--o-forum_ps] [--o-forum_smg]
            [--o-gofile] [--o-hex] [--o-hload] [--o-ibam] [--o-ibb] [--o-imgbox] [--o-imghaha] [--o-imgtwist] [--o-jpgchurch] [--o-lovefap] [--o-mega] [--o-pixl]
            [--o-pxdrain] [--o-pxhost] [--o-sendvid] [--o-simpcity] [--o-streamlare] [--o-streamtape] [--o-voe] [--o-xvids] [--test]
            album_name [url]

positional arguments:
  album_name            Name of the outpuf folder.
  url                   URL to scrape.

options:
  -h, --help            show this help message and exit
  -a FILE, --batch-file FILE
                        File containing URLs to download ('-' for stdin), one URL per line. Lines starting with '#', ';' or ']' are considered as comments and
                        ignored.
  -u, --save-urls       Provided the flag, all direct urls for content will be saved into txtfile in the output folder. (default=False)
  --version             Print program version and exit
  --supported-sites     Show supported sites.
  -d, --debug           Enable debug mode.
  --page-limit CRAWL_PAGE_LIMIT
                        Limit number of pages scraped when crawling.

Download Options:
  --omit-download       Skip downloading files, useful when just scraping links like mega.nz or when debugging and don't want to download.
  --skip-existing       Skips items with colliding names.By default the duplicate items are downloaded with integer added to the name.
  --overwrite-existing  Ovewrites items with duplicate names.By default differentiates items by appending integer to the filename.
  --download-path DOWNLOAD_PATH
                        Provide custom download path.
  -s, --separate-content
                        Provided the flag, downloaded items will be separated into corresponding folders.
  --skip-vid            Skip download of videos.
  --skip-img            Skip download of images.
  --skip-audio          Skip download of audio tracks.
  --skip-archive        Skip download of archives.

Disable Scraper:
  --d-anon              Disable Anon
  --d-bunkr             Disable Bunkr
  --d-cdrop             Disable Cdrop
  --d-erome             Disable Erome
  --d-forum_lm          Disable Forum_Lm
  --d-forum_nstar       Disable Forum_Nstar
  --d-forum_ps          Disable Forum_Ps
  --d-forum_smg         Disable Forum_Smg
  --d-gofile            Disable Gofile
  --d-hex               Disable Hex
  --d-hload             Disable Hload
  --d-ibam              Disable Ibam
  --d-ibb               Disable Ibb
  --d-imgbox            Disable Imgbox
  --d-imghaha           Disable Imghaha
  --d-imgtwist          Disable Imgtwist
  --d-jpgchurch         Disable Jpgchurch
  --d-lovefap           Disable Lovefap
  --d-mega              Disable Mega
  --d-pixl              Disable Pixl
  --d-pxdrain           Disable Pxdrain
  --d-pxhost            Disable Pxhost
  --d-sendvid           Disable Sendvid
  --d-simpcity          Disable Simpcity
  --d-streamlare        Disable Streamlare
  --d-streamtape        Disable Streamtape
  --d-voe               Disable Voe
  --d-xvids             Disable Xvids

Specify Extractors to use:
  --o-anon              Select Anon for use.
  --o-bunkr             Select Bunkr for use.
  --o-cdrop             Select Cdrop for use.
  --o-erome             Select Erome for use.
  --o-forum_lm          Select Forum_Lm for use.
  --o-forum_nstar       Select Forum_Nstar for use.
  --o-forum_ps          Select Forum_Ps for use.
  --o-forum_smg         Select Forum_Smg for use.
  --o-gofile            Select Gofile for use.
  --o-hex               Select Hex for use.
  --o-hload             Select Hload for use.
  --o-ibam              Select Ibam for use.
  --o-ibb               Select Ibb for use.
  --o-imgbox            Select Imgbox for use.
  --o-imghaha           Select Imghaha for use.
  --o-imgtwist          Select Imgtwist for use.
  --o-jpgchurch         Select Jpgchurch for use.
  --o-lovefap           Select Lovefap for use.
  --o-mega              Select Mega for use.
  --o-pixl              Select Pixl for use.
  --o-pxdrain           Select Pxdrain for use.
  --o-pxhost            Select Pxhost for use.
  --o-sendvid           Select Sendvid for use.
  --o-simpcity          Select Simpcity for use.
  --o-streamlare        Select Streamlare for use.
  --o-streamtape        Select Streamtape for use.
  --o-voe               Select Voe for use.
  --o-xvids             Select Xvids for use.

Test Options:
  --test                Run as a test, outputs the scraped items to stdout as dictionary.
   ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->
## Contributing

Any contributions you make are appreciated.

If you have a suggestion that would make this project better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/NewFeature`)
3. Commit your Changes (`git commit -m 'Add some NewFeature'`)
4. Push to the Branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Vladimír Polák - vladimirpolak2@gmail.com - Dio#7865

Project Link: [https://github.com/vladimirpolak/lols](https://github.com/vladimirpolak/lols)

<p align="right">(<a href="#readme-top">back to top</a>)</p>