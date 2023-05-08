from typing import Union
from enum import Enum


class ContentType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    ARCHIVE = 'archive'
    M3U8 = 'm3u8'
    URL = 'url'

    @classmethod
    def from_str(cls, string_repr: str):
        return cls(string_repr)


class Item:
    source: str
    filename: str
    extension: str  # .jpg/.mp4...
    content_type: ContentType
    album_title: Union[str, None]
    headers_: Union[dict, None]

    def __init__(self, source: str, filename: str, extension: str, content_type: ContentType,
                 album_title: str = None,
                 headers: dict = None,
                 req_kwargs: dict = None):
        self.source = source
        self.filename = filename
        self.extension = extension
        self.content_type = content_type
        self.album_title = album_title
        self._headers = headers
        self._req_kwargs = req_kwargs

    @property
    def headers(self):
        return self._headers or {}

    @headers.setter
    def headers(self, headers: dict):
        self._headers = headers

    @property
    def req_kwargs(self):
        return self._req_kwargs or {}

    @req_kwargs.setter
    def req_kwargs(self, req_kwargs):
        self._req_kwargs = req_kwargs

    def to_dict(self):
        item_dict = {
            'source': self.source,
            'filename': self.filename,
            'extension': self.extension,
            'content_type': self.content_type.value,
            'album_title': self.album_title,
            'headers': self._headers,
            'req_kwargs': self._req_kwargs,
        }
        return {k: v for k, v in item_dict.items() if v is not None}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(source=data.get("source"),
                   filename=data.get("filename"),
                   extension=data.get("extension"),
                   content_type=ContentType(data.get("content_type")),
                   headers=data.get("headers", None),
                   album_title=data.get("album_title", None),
                   req_kwargs=data.get("req_kwargs", None)
                   )

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



