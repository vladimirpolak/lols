from typing import List
from pathlib import Path
from collections import defaultdict
from downloader import Item
import json
import base64
import os


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
        print("Saved URLs to {}".format(str(file_path)))

    with open(str(file_path), "w") as f:
        f.write("\n".join(links))


def load_file(path: str) -> list:
    """Opens the provided file as list of lines."""
    try:
        with open(path, "r") as file:
            output = [
                line.strip()
                for line in file.readlines()
                if not (line.startswith("#")
                        or line.startswith("//"))
            ]
    except FileNotFoundError:
        raise Exception("Provided file doesn't exist!")
    else:
        return output


def clear_output(lines_to_clear: int = 1):
    for _ in range(lines_to_clear):
        LINE_UP = '\033[1A'
        LINE_CLEAR = '\x1b[2K'
        print(LINE_UP, end=LINE_CLEAR)
    # os.system('cls' if os.name == 'nt' else 'clear')


def print_data(data: List[Item]):
    data_count = defaultdict(int)
    for item in data:
        data_count[item.content_type] += 1

    print("-" * 50)
    for content_type, count in data_count.items():
        print(f"Number of {content_type}s scraped: {count}")
    print("-" * 50)


def dump_curr_session(cookies: dict, items_to_download: List[Item]):
    output = dict()
    output["cookies"] = cookies
    output["items"] = [item.__dict__ for item in items_to_download]

    with open("terminated_session.json", "w") as outfile:
        json.dump(output, outfile, indent=4)


def decode_base64(input_str: str):
    return base64.b64decode(input_str).decode()


def slugify(input_str: str):
    return input_str.lower().replace(" ", "-")

