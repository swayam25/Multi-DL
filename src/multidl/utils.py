import base64
import requests
from .term import Print
from mutagen.flac import Picture
from mutagen.mp4 import MP4, MP4Tags
from mutagen.oggvorbis import OggVorbis
from typing import Literal


def sanitize_path(path: str) -> str:
    """Replace illegal filename characters except for safe path usage."""
    illegal_chars = ["/", "\\"]
    for ch in illegal_chars:
        path = path.replace(ch, "|")
    path = path.replace("%dir%", "/")
    return path


class YTOptions:
    """
    Get the options for yt-dlp.

    Args:
        type: The type of media to download.
        dir: The directory to save the file.
        filename: The filename to save the file as.
        progress_hooks: A list of progress hooks to use.
    """

    def __init__(
        self,
        type: Literal["audio", "video", "default"] = "default",
        dir: str = ".",
        filename: str = "%(title)s",
        progress_hooks: list | None = None,
    ):
        self.yt_opts: dict = {}

        safe_dir = sanitize_path(dir)
        safe_filename = sanitize_path(filename)

        yt_options = {
            "quiet": True,
            "noprogress": True,
            "ignoreerrors": True,
            "format": "bv*+ba[ext=mp4]/best",
            "outtmpl": f"{safe_dir}/{safe_filename}.%(ext)s",
            "postprocessors": [],
        }
        if type == "audio":
            yt_options["format"] = "ba[ext=m4a]/ba"
            yt_options["postprocessors"].append(
                {"key": "FFmpegExtractAudio", "preferredcodec": "vorbis", "preferredquality": "0"}
            )
        elif type == "video":
            yt_options["format"] = "bv[ext=mp4]/bv"
            yt_options["postprocessors"].append(
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            )
        else:
            yt_options["postprocessors"].append(
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            )
        if progress_hooks:
            yt_options["progress_hooks"] = progress_hooks
        self.yt_options = yt_options

    def get(self) -> dict:
        """Get the options for yt-dlp."""
        return self.yt_options


class AddMetaData:
    """
    Add metadata to the file.

    Args:
        file: The file to add metadata to.
        artist: The artist name of the file.
        album: The album name of the file.
        art: The cover art url of the file.
    """

    def __init__(self, file: str, artist: str, album: str, art: str):
        if file.endswith(".ogg"):
            audio = OggVorbis(file)
            img: bytes = requests.get(art).content

            pic = Picture()
            pic.data = img
            pic.type = 17
            pic.desc = "Cover Art"
            pic.mime = "image/jpeg"

            pic_data = pic.write()
            encoded_data = base64.b64encode(pic_data)
            vcomment_value = encoded_data.decode("ascii")

            audio["metadata_block_picture"] = [vcomment_value]
            audio["coverart"] = [vcomment_value]
            audio["album"] = album
            audio["artist"] = artist
            audio.save()

        elif file.endswith(".mp4"):
            video = MP4(file)
            if video.tags is None:
                video.tags = MP4Tags()
            video.tags["\xa9alb"] = album
            video.tags["\xa9ART"] = artist
            video.tags["covr"] = [requests.get(art).content]
            video.save()

        else:
            Print.error(f'".{file.split(".")[-1]}" is not a supported file type.')
            Print.warn("Please use [cyan].ogg[/] or [cyan].mp4[/] files.")
            exit()
