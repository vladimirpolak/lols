from .downloader import Downloader, HttpClient
from .m3u8_downloader import M3u8Downloader
from .models import Item, ContentType

from pathlib import Path
import logging


def download_item(item: Item, download_path: Path, session, verbose: bool):
    if item.content_type in [
            ContentType.IMAGE,
            ContentType.VIDEO,
            ContentType.AUDIO,
            ContentType.ARCHIVE]:
        dl = Downloader(session)
        try:
            dl.download_item(item, download_path, verbose)
        except Exception as e:
            logging.error(f"Failed downloading '{item.source}', error: {e}")
    if item.content_type == ContentType.M3U8:
        dl = M3u8Downloader(
            url=item.source,
            output_filename=download_path,
            session=session
        )

        dl.start()