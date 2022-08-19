from .types import ContentType


class Item:
    content_type: ContentType
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



