from .http import Item, ContentType
from pathlib import Path
from typing import Union


class PathCreator:
    IMAGES_DIR_NAME = "Images"
    VIDEOS_DIR_NAME = "Videos"
    ARCHIVES_DIR_NAME = "Archives"
    AUDIO_DIR_NAME = "Audio"

    @classmethod
    def generate_download_path(
            cls,
            album_folder: str,
            download_item: Item,
            skip_existing: bool,
            overwrite_existing: bool,
            separate_content: bool) -> Union[Path, None]:

        output_folder = cls._create_path(album_folder)

        if download_item.content_type == ContentType.URL:
            return None

        if separate_content:
            output_folder = output_folder / cls.content_dir(download_item.content_type)

        if not output_folder.exists():
            output_folder.mkdir(parents=True)

        file_path = output_folder / (download_item.filename + download_item.extension)

        if file_path.exists():
            if skip_existing is True:
                return None
            else:
                if overwrite_existing:
                    file_path = output_folder / (download_item.filename + download_item.extension)
                else:
                    step: int = 1
                    while True:
                        file_path = output_folder / (
                                f'{download_item.filename} ({step})' + download_item.extension
                        )
                        if not file_path.exists():
                            break
                        step += 1
        return file_path

    @classmethod
    def content_dir(cls, content_type: ContentType) -> str:
        return {
            ContentType.IMAGE: cls.IMAGES_DIR_NAME,
            ContentType.VIDEO: cls.VIDEOS_DIR_NAME,
            ContentType.M3U8: cls.VIDEOS_DIR_NAME,
            ContentType.ARCHIVE: cls.ARCHIVES_DIR_NAME,
            ContentType.AUDIO: cls.AUDIO_DIR_NAME
        }[content_type]


    @staticmethod
    def _create_path(dirname_or_absolutepath: str):
        path = Path(dirname_or_absolutepath)
        if path.is_absolute():
            return path
        else:
            return Path().cwd() / dirname_or_absolutepath
