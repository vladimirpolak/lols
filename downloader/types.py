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


def determine_content_type_(filename: str) -> str:
    filename = filename.lower()

    if any([filename.endswith(ext) for ext in img_extensions]):
        return "image"
    elif any([filename.endswith(ext) for ext in vid_extensions]):
        return "video"
    elif any([filename.endswith(ext) for ext in archive_extensions]):
        return "archive"
    raise ContentTypeError(f"Unknown extension '{filename}'!")
