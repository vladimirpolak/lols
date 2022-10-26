from exceptions import ContentTypeError
from enum import Enum, auto

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
img_extensions = img_extensions + [ext.upper() for ext in img_extensions]

vid_extensions = [
    ".mp4",
    ".mov",
    ".m4v",
    ".webm",
    ".avi",
    ".wmv",
    ".flv",
    ".mkv",
    ".ts"
]
vid_extensions = vid_extensions + [ext.upper() for ext in vid_extensions]

archive_extensions = [
    ".zip",
    ".zipx",
    ".rar",
    ".7z"
]
archive_extensions = archive_extensions + [ext.upper() for ext in archive_extensions]


audio_extensions = [
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".wma",
    ".aac"
]
audio_extensions = audio_extensions + [ext.upper() for ext in audio_extensions]


class ContentType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    ARCHIVE = 'archive'
    M3U8 = 'm3u8'

    @classmethod
    def from_str(cls, string_repr: str):
        return cls(string_repr)


def determine_content_type_(filename: str) -> ContentType:
    filename = filename.lower()

    if any([filename.endswith(ext) for ext in img_extensions]):
        return ContentType.IMAGE
    elif any([filename.endswith(ext) for ext in vid_extensions]):
        return ContentType.VIDEO
    elif any([filename.endswith(ext) for ext in archive_extensions]):
        return ContentType.ARCHIVE
    elif any([filename.endswith(ext) for ext in audio_extensions]):
        return ContentType.AUDIO
    elif filename.endswith('m3u8'):
        return ContentType.M3U8
    raise ContentTypeError(f"Unknown extension '{filename}'!")

