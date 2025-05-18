import inspect
import re
import shutil
from . import Spotify, YouTube
from .term import Print
from typing import Literal


class MultiDL:
    """
    Core class for Multi DL.

    Args:
        query: The query string to be used for searching.
    """

    def __init__(self, query: str | None = None):
        path = shutil.which("ffmpeg")
        if not path:
            Print.error("FFmpeg is not installed")
            Print.warn(
                "Please install [link=https://ffmpeg.org/download.html bold cyan]FFmpeg[/] to use [cyan]multidl[/]"
            )
            exit()
        self.query = query
        if self.query:
            self.query = re.sub(
                r"(youtu\.be/|youtube\.com/shorts/|music\.youtube\.com/watch)",
                "youtube.com/watch?v=",
                self.query,
            )
            self.query = self.query.split("&")[0]

    def _dispatch_handler(self, handlers: dict, formatter: str, args: dict | None = None):
        """
        Dispatches the appropriate handler based on the query and a custom formatter.

        Args:
            handlers: Mapping of key substrings to (handler object, keywords list) tuples.
            formatter: Formatter string for the function name, e.g. "info_{f}" or "download_{f}". "{f}" refers to the function name in the keyword.
            args: Optional argument(s) to pass to the handler function.

        Returns:
            bool: True if a handler was found and executed, False otherwise.
        """
        for key, (handler_obj, keywords) in handlers.items():
            if key in self.query:
                obj = handler_obj() if callable(handler_obj) else handler_obj
                for keyword in keywords:
                    if ":" in keyword:
                        match_key, func_name = keyword.split(":", 1)
                    else:
                        match_key, func_name = keyword, keyword
                    if match_key in self.query:
                        func = getattr(obj, formatter.format(f=func_name), None)
                        if func:
                            sig = inspect.signature(func)
                            param_names = list(sig.parameters.keys())
                            matched_args = []
                            if args:
                                for param in param_names:
                                    for arg in args:
                                        if param == arg:
                                            matched_args.append(args[param])
                                            break
                                if matched_args:
                                    func(*matched_args)
                                else:
                                    func(*args)
                            else:
                                func()
                            return True
        return False

    def info(self):
        """Get info about the media."""
        if not self.query:
            Print.error("Query is empty")
            exit(1)
        yt = YouTube(self.query)
        handlers = {
            "youtube.com": (yt, ["playlist:pl", "watch:video", "channel", "/@:channel"]),
            "open.spotify.com": (
                lambda: Spotify(self.query),  # type: ignore
                ["album", "track", "playlist:pl", "user"],
            ),
        }
        if not self._dispatch_handler(handlers, formatter="info_{f}"):
            yt.info_search()

    def download(
        self,
        type: Literal["audio", "video", "default"] = "default",
        threads: int | Literal["max"] = 5,
    ):
        """Download the media."""
        if not self.query:
            Print.error("Query is empty")
            exit(1)
        yt = YouTube(self.query)
        handlers = {
            "youtube.com": (yt, ["playlist:pl", "watch:video", "channel", "/@:channel"]),
            "open.spotify.com": (
                lambda: Spotify(self.query),  # type: ignore
                ["album", "track", "playlist:pl", "user"],
            ),
        }
        if not self._dispatch_handler(
            handlers,
            formatter="download_{f}",
            args={
                "type": type,
                "threads": threads,
            },
        ):
            yt.download_search(type, threads)
