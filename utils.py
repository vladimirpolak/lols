import logging
import json
import base64

from typing import List
from pathlib import Path
from collections import defaultdict
from downloader.models import Item
from console import console
from datetime import datetime


def split_filename_ext(file) -> tuple:
    """
    Splits file into filename and its extension.

    :param file: str
    :return: Tuple[str(filename), str(extension)]
    """
    filename = ".".join(file.split(".")[:-1])
    extension = "." + file.split('.')[-1]

    return filename, extension


def save_links(
        links: List[str],
        output_path: Path,
        filename: str,
        debug: bool
):
    file_path = output_path / filename

    if debug:
        console.print("Saved URLs to {}".format(str(file_path)))

    with open(str(file_path), "w") as f:
        f.write("\n".join(links))


def save_to_file(file: Path, data: str):
    if not file.parent.exists():
        file.parent.mkdir(parents=True)
    try:
        with file.open("a", encoding='utf-8') as f:
            f.write(data)
            f.write("\n")
    except ValueError as e:
        logging.debug(f"{e}\nFailed to write '{data}' to file at '{file}'.")


def load_file(path: Path) -> list:
    """Opens the provided file as list of lines."""
    try:
        with path.open("r") as file:
            output = [
                line.strip()
                for line in file.readlines()
                if not (line.startswith("#")  # Commented lines
                        or line.startswith("//"))
            ]
    except FileNotFoundError:
        raise Exception("Provided file doesn't exist!")
    else:
        return output


def print_data(data: List[Item]):
    data_count = defaultdict(int)
    for item in data:
        data_count[item.content_type] += 1

    console.rule("[green]-SCRAPED", align="left")
    for content_type, count in data_count.items():
        console.print(f"{count} {content_type.name.lower()}s.")


def dump_curr_session(
        cookies: dict,
        items_to_download: List[Item],
        filename: str = "terminated_session"
):
    data = dict()
    data["cookies"] = cookies
    data["items"] = [item.__dict__() for item in items_to_download]

    with open(f"{filename}.json", "w") as outfile:
        json.dump(data, outfile, indent=4)


def decode_base64(input_str: str):
    return base64.b64decode(input_str).decode()


def delete_special_chars(input_str: str):
    special_chars = r"""!@#$%^+=`"',.;?~\/*<>()[]{}'\:"""
    for char in special_chars:
        input_str = input_str.replace(char, "")
    input_str = input_str.replace("&", "and")
    return input_str


def slugify(input_str: str, sep: str = "-", del_special_chars: bool = False):
    slugified = input_str.lower().replace(" ", sep)
    if del_special_chars:
        return delete_special_chars(slugified)
    return slugified


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