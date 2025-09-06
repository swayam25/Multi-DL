from typing import Literal


class SuppressLogger:
    """Custom logger to suppress all yt-dlp output including warnings."""

    def debug(self, msg):
        """Suppress debug messages."""
        pass

    def info(self, msg):
        """Suppress info messages."""
        pass

    def warning(self, msg):
        """Suppress warning messages."""
        pass

    def error(self, msg):
        """Suppress error messages."""
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

        yt_options = {
            "quiet": True,
            "noprogress": True,
            "ignoreerrors": True,
            "no_warnings": True,
            "logger": SuppressLogger(),
            "logtostderr": False,
            "format": "bv*+ba[ext=mp4]/best",
            "outtmpl": f"{safe_dir}/{safe_filename}.%(ext)s",
            "postprocessors": [],
        }
        if subtitles and type != "audio":  # Embed subtitles only for video or default type
            yt_options["writesubtitles"] = True
            yt_options["writeautomaticsub"] = True
            yt_options["subtitleslangs"] = list(subtitles)
            yt_options["postprocessors"].append({"key": "FFmpegEmbedSubtitle"})
        if type == "audio":  # Download audio only
            yt_options["format"] = "ba[ext=m4a]/ba"
            yt_options["postprocessors"].append(
                {"key": "FFmpegExtractAudio", "preferredcodec": "vorbis", "preferredquality": "0"}
            )
        else:
            if type == "video":  # Download video only
                yt_options["format"] = "bv[ext=mp4]/bv"
            yt_options["postprocessors"].append(
                {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
            )
        # Embed thumbnail and metadata in both audio and video
        yt_options["postprocessors"].extend(
            [
                {"key": "EmbedThumbnail"},
                {"key": "FFmpegMetadata"},
            ]
        )
        if progress_hooks:
            yt_options["progress_hooks"] = progress_hooks
        self.yt_options = yt_options

    def get(self) -> dict:
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
        return info_dict
