<h1 style="text-align: center;">lols</h1>

<!-- ABOUT THE PROJECT -->
## About

Goal of this project is to have Bulk downloader/Content scraper capable of scraping content
from multiple hosting sites/forums. Simple concept: user inputs a page url and scraper downloads it's contents.

<!-- GETTING STARTED -->
## Getting Started

There are 2 main ways to use the script:
* Download an executable bundle from [here](https://www.example.com) and run in terminal.
* Clone this repo and install required packages. You will need [python](https://www.python.org/downloads/) and [git](https://git-scm.com/downloads) installed on your pc.

### Executable
_Using executable_
1. Download bundled executable from [here](https://www.example.com).
2. In command line navigate to the folder containing the app.
3. Run the program
   ```sh
   lols [url] [options]
   ```

### Git clone

_Use of git clone and python enviroment_

1. Download and install latest [python](https://www.python.org/downloads/) and [git](https://git-scm.com/downloads).
2. In command line navigate to the folder where you want the application and clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
3. Navigate to the project folder
   ```sh
   cd Project-Name
   ```
4. Install python dependencies
   ```sh
   pip install -r requirements.txt
   ```
5. Run the program
   ```sh
   lols.py [url] [options]
   ```



<!-- USAGE EXAMPLES -->
## Usage
Basic usage syntax is as follows:
   ```
   [program] [url] [options]
   ```

### Options
   ```
  -h, --help                                 Show help and exit.
            
  -a [file.txt], --batch-file [file.txt]     (alpha)File containing URLs to download, one URL per line.
                                              Lines starting with '#', ';' or ']' are considered as comments and ignored.
            
  -s, --separate-content                     Provided the flag, downloaded content will NOT be separated in folders based on content type.
            
  -u, --save-urls                            Provided the flag, all direct urls for content will be saved into txtfile in the output folder.
  --version                                  Print program version and exit
  --supported-sites                          Print supported sites and exit
   ```




<!-- SUPPORTED SITES -->
## Supported sites
View supported sites [here](docs/supported_sites.txt)



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Vladimír Polák - vladimirpolak2@gmail.com - Dio#7865

Project Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)
