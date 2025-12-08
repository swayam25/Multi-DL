from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from yt_dlp import _Params


class SuppressLogger:
    """Custom logger to suppress all yt-dlp output including warnings."""

    def __init__(self, ydl=None):
        """Initialize logger with optional ydl parameter."""
        pass

    def debug(self, *args, **kwargs):
        """Suppress debug messages."""
        pass

    def info(self, *args, **kwargs):
        """Suppress info messages."""
        pass

    def warning(self, *args, **kwargs):
        """Suppress warning messages."""
        pass

    def error(self, *args, **kwargs):
        """Suppress error messages."""
        pass

    def stdout(self, *args, **kwargs):
        """Suppress stdout messages."""
        pass

    def stderr(self, *args, **kwargs):
        """Suppress stderr messages."""
        pass


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

    Parameters:
        type: The type of media to download.
        subtitles: List of subtitles to download.
        dir: The directory to save the file.
        filename: The filename to save the file as.
        progress_hooks: A list of progress hooks to use.
    """

    def __init__(
        self,
        type: Literal["audio", "video", "default"] = "default",
        subtitles: list[str] | None = None,
        dir: str = ".",
        filename: str = "%(title)s",
        progress_hooks: list | None = None,
    ):
        self.yt_opts: dict = {}

        safe_dir = sanitize_path(dir)
        safe_filename = sanitize_path(filename)
        postprocessors: list = []

        if subtitles and type != "audio":  # Embed subtitles only for video or default type
            postprocessors.append({"key": "FFmpegEmbedSubtitle"})

        if type == "audio":  # Download audio only
            format_str = "ba[ext=m4a]/ba"
            postprocessors.append(
                {"key": "FFmpegExtractAudio", "preferredcodec": "vorbis", "preferredquality": "0"}
            )
        else:
            if type == "video":  # Download video only
                format_str = "bv[ext=mp4]/bv"
            else:
                format_str = "bv*+ba[ext=mp4]/best"
            postprocessors.append({"key": "FFmpegVideoConvertor", "preferedformat": "mp4"})

        # Embed thumbnail and metadata in both audio and video
        postprocessors.extend(
            [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        )

        yt_options: "_Params" = {  # noqa: UP037
            "quiet": True,
            "noprogress": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "logger": SuppressLogger(),
            "logtostderr": False,
            "format": format_str,
            "outtmpl": f"{safe_dir}/{safe_filename}.%(ext)s",
            "postprocessors": postprocessors,
        }

        if subtitles and type != "audio":
            yt_options |= {
                "writesubtitles": True,
                "writeautomaticsub": True,
                "subtitleslangs": list(subtitles),
            }
        if progress_hooks:
            yt_options["progress_hooks"] = progress_hooks
        self.yt_options = yt_options

    def get(self) -> "_Params":
        """Get the options for yt-dlp."""
        return self.yt_options

    @staticmethod
    def inject_metadata(
        info_dict: dict, title: str = "", artist: str = "", album: str = "", cover_url: str = ""
    ) -> dict:
        """
        Inject custom metadata into yt-dlp info dictionary.

        Parameters:
            info_dict: The yt-dlp info dictionary to modify.
            title: Title to set.
            artist: Artist name to set.
            album: Album name to set.
            cover_url: Cover art URL to set.

        Returns:
            Modified info dictionary
        """
        if title:
            info_dict["title"] = title
        if artist:
            info_dict["meta_artist"] = artist
        if album:
            info_dict["meta_album"] = album
        if cover_url:
            info_dict["thumbnails"] = [
                {
                    "url": cover_url,
                    "id": "custom_cover",
                    "preference": 1000,  # High preference to ensure it's selected
                },
            ]
            info_dict["thumbnail"] = cover_url
        return info_dict
