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
img_extensions = img_extensions + [ext.upper() for ext in img_extensions]

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


def determine_content_type_(filename: str) -> str:
    filename = filename.lower()

    if any([filename.endswith(ext) for ext in img_extensions]):
        return "image"
    elif any([filename.endswith(ext) for ext in vid_extensions]):
        return "video"
    elif any([filename.endswith(ext) for ext in archive_extensions]):
        return "archive"
    elif any([filename.endswith(ext) for ext in audio_extensions]):
        return "audio"
    raise ContentTypeError(f"Unknown extension '{filename}'!")
