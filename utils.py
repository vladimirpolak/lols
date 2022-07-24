from typing import List
from pathlib import Path


def split_filename_ext(file) -> tuple:
    """
    Splits file into filename and its extension.

    :param file: str
    :return: Tuple[str(filename), str(extension)]
    """
    filename = ".".join(file.split(".")[:-1])
    extension = f".{file.split('.')[-1]}"

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
