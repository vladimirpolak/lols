from .types import ContentType
from typing import Union


class Item:
    source: str
    filename: str
    extension: str  # .jpg/.mp4...
    content_type: ContentType
    album_title: Union[str, None]
    headers_: Union[dict, None]

    def __init__(self, source: str, filename: str, extension: str, content_type: ContentType,
                 album_title: str = None,
                 headers: dict = None):
        self.source = source
        self.filename = filename
        self.extension = extension
        self.content_type = content_type
        self.album_title = album_title
        self.headers_ = headers

    @property
    def headers(self):
        return self.headers_ or {}

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



