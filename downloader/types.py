from exceptions import ContentTypeError


img_extensions = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".tiff",
    ".tif",
    ".svg",
    ".svgz"
]

vid_extensions = [
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
    ".avi",
    ".wmv",
    ".flv",
    ".mkv"
]

archive_extensions = [
    ".zip",
    ".zipx",
    ".rar",
    ".7z"
]


class Item:
    content_type: str  # image/video/archive
    album_title: str
    filename: str
    extension: str  # .jpg/.mp4...
    source: str

    def __init__(self, content_type: str, filename: str, extension: str, source: str, album_title: str = None):
        self.content_type = content_type
        self.album_title = album_title
        self.filename = filename
        self.extension = extension
        self.source = source

    def __str__(self):
        return f"Item(" \
               f"{self.filename}{self.extension}, " \
               f"{self.source}" \
               f")"

    def __repr__(self):
        return f"Item(" \
               f"content_type={self.content_type}, " \
               f"album_title={self.album_title}, " \
               f"filename={self.filename}, " \
               f"extension={self.extension}, " \
               f"source={self.source}" \
               f")"


def determine_content_type_(filename: str) -> str:
    filename = filename.lower()

    if any([filename.endswith(ext) for ext in img_extensions]):
        return "image"
    elif any([filename.endswith(ext) for ext in vid_extensions]):
        return "video"
    elif any([filename.endswith(ext) for ext in archive_extensions]):
        return "archive"
    raise ContentTypeError(f"Unknown extension '{filename}'!")
