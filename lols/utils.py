from .http.models import Item

from urllib.parse import unquote
from datetime import datetime
from pathlib import Path
from typing import Tuple, List, Union, Iterable

import w3lib
import logging
import base64
import json


Filename = str
Extension = str

comment_symbols = ["#", "//"]


def split_filename_ext(file) -> Tuple[Filename, Extension]:
    """
    Splits file into filename and its extension.

    :param file: str
    :return: Tuple[str(filename), str(extension)]
    """
    filename = ".".join(file.split(".")[:-1])
    extension = "." + file.split('.')[-1]

    return filename, extension


def save_to_file(file: Path, data: str):
    if not file.parent.exists():
        file.parent.mkdir(parents=True)
    try:
        with file.open("a", encoding='utf-8') as f:
            f.write(data)
            f.write("\n")
    except ValueError as e:
        logging.debug(f"{e}\nFailed to write '{data}' to file at '{file}'.")


def is_comment(line: str) -> bool:
    return any([line.startswith(symbol) for symbol in comment_symbols])


def load_file(path: Path, handle_comments: bool = True) -> Iterable:
    """Opens the provided file as list of lines."""
    try:
        with path.open("r") as file:
            for line in file.readlines():
                if handle_comments and is_comment(line):
                    continue
                yield line.strip()
    except FileNotFoundError:
        raise Exception("Provided file doesn't exist!")


def dump_curr_session(
        cookies: dict,
        items_to_download: List[Item],
        filename: str = "terminated_session"
):
    data = dict()
    data["cookies"] = cookies
    data["items"] = [item.__dict__() for item in items_to_download]

    with open(f"{filename}.json", "w", encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)


def decode_base64(input_str: str):
    return base64.b64decode(input_str).decode()


def url_params_to_dict(params: str) -> Union[dict, None]:
    """
    key=value&key=value -> {key: value, key: value}
    :param params: str
    :return: dict
    """
    try:
        output = {item.split("=")[0]: item.split("=")[-1] for item in unquote(params).split("&")}
    except IndexError:
        return None
    else:
        return output


def delete_special_chars(input_str: str):
    special_chars = r"""!@#$%^+=`"',.;?~\/*<>()[]{}'\:"""
    for char in special_chars:
        input_str = input_str.replace(char, "")
    input_str = input_str.replace("&", "and")
    return input_str


def slugify(input_str: str, sep: str = "-", del_special_chars: bool = False, replace_entities: bool = False):
    output = input_str.lower().replace(" ", sep)
    if replace_entities:
        output = w3lib.html.replace_entities(output)
    if del_special_chars:
        output = delete_special_chars(output)

    return output


def curr_time(format: str = "%Y-%m-%d-%H-%M"):
    return datetime.now().strftime(format)


def logs_setup(
        debug: bool,
        logs_directory: str = "logs",
        log_filename: str = str(curr_time())
):
    log_filename = f"{log_filename}.log"
    if logs_directory:
        log_dir = Path().cwd() / logs_directory
        if not log_dir.exists():
            log_dir.mkdir()
        log_path = log_dir / log_filename
    else:
        log_path = Path.cwd() / log_filename

    logging.basicConfig(
        handlers=[logging.FileHandler(str(log_path), 'w', 'utf-8'), logging.StreamHandler()],
        level=logging.DEBUG if debug else logging.INFO,
        format='%(levelname)s %(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S',
    )


def get_supported_sites(scraper_classes: list) -> list:
    all_sites = []
    for scraper in scraper_classes:
        domain = scraper.DOMAIN
        description = scraper.DESC.title()
        codename = scraper.CODENAME
        # url = "example url undefined"
        # if scraper.SAMPLE_URLS:
        #     url = scraper.SAMPLE_URLS[0]

        site_info = f"{description}\n" \
                    f"--codename: {codename}\n" \
                    f"--domain: {domain}\n" \
                    # f"--example url: {url}"
        all_sites.append(site_info)
    return all_sites