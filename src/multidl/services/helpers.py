import os
from ..term import Print, ProgressBar
from ..utils import AddMetaData, YTOptions
from dataclasses import dataclass
from rich.progress import TaskID
from threading import Thread
from typing import Literal, NotRequired, TypedDict
from yt_dlp import YoutubeDL


class YTDownloader:
    """
    Downloader class for downloading media. Uses yt-dlp to download media from YouTube.

    Args:
        query: The query string to be used for searching.
        type: The type of media to download.
        playlist: The playlist folder name to save the media to.
        album: The album name of the media.
        title: The title of the media.
        art: The cover art url of the media.
        artist: The artist of the media.
        progress: A progress bar to use for downloading.
    """

    def __init__(
        self,
        query: str,
        title: str,
        type: Literal["audio", "video", "default"] = "default",
        album: str = "",
        playlist: str = ".",
        art: str = "",
        artist: str = "",
        progress: ProgressBar | None = None,
    ):
        self.query = query
        self.type: Literal["audio", "video", "default"] = type
        self.album = album
        self.playlist = playlist
        self.art = art
        self.artist = artist
        self.progress = progress
        self.title = title
        self._title = title if len(title) < 20 else title[:20].strip() + "..."

    def download(self):
        if self.progress is not None:
            self.task = self.progress.download.add_task(
                description=f"[yellow]Downloading[/] [cyan]{self._title}[/]",
                total=0,
                start=False,
            )
        is_url: bool = (
            self.query.startswith("http") or self.query.startswith("www")
        ) and "youtube" in self.query
        yt_opts = YTOptions(self.type, self.playlist, self.title, progress_hooks=[self.hook]).get()
        with YoutubeDL(yt_opts) as ydl:
            yt = ydl.extract_info(f"ytsearch:{self.query}" if not is_url else self.query)
        if not yt:
            Print.error(f"No results found for the query [cyan]{self.query}[/].")
            exit(1)
        file_entry = yt["entries"][0] if isinstance(yt, dict) and "entries" in yt else yt
        if file_entry:
            AddMetaData(
                file_entry["requested_downloads"][0]["filepath"],
                self.artist if self.artist else file_entry["uploader"],
                self.album
                if self.album
                else (
                    file_entry["playlist"]
                    if "playlist" in file_entry and file_entry["playlist"]
                    else ""
                ),
                self.art if self.art else file_entry["thumbnails"][0]["url"],
            )

    def hook(self, d):
        """Hook for yt-dlp to update the progress bar."""
        if self.progress is not None:
            self.progress.download.start_task(self.task) if "total_bytes" in d else None
            if d["status"] == "downloading":
                self.progress.download.update(
                    self.task,
                    total=d["total_bytes"] if "total_bytes" in d else d["downloaded_bytes"] + 1,
                    completed=d["downloaded_bytes"],
                )
            elif d["status"] == "finished":
                self.progress.download.update(
                    self.task,
                    description=f"[green]Downloaded[/] [cyan]{self._title}[/]",
                )
                self.progress = None


@dataclass
class DownloadTaskSchema(TypedDict):
    query: str
    title: str
    type: NotRequired[str]
    album: NotRequired[str]
    playlist: NotRequired[str]
    art: NotRequired[str]
    artist: NotRequired[str]


class Downloader:
    """Helper class for downloading media, supporting both single and parallel downloads."""

    def __init__(
        self,
        tasks: DownloadTaskSchema | list[DownloadTaskSchema],
        progress: ProgressBar | None = None,
        playlist_task: TaskID | None = None,
        threads: int | Literal["max"] = 5,
    ):
        """
        Args:
            tasks: Single or multiple download tasks.
            progress: Progress bar instance.
            playlist_task: Task ID for playlist progress.
            threads: Number of threads to use, or 'max' for all available. Default is 5.
        """
        self.tasks = self._filter_tasks(tasks)
        self.progress = progress
        self.playlist_task = playlist_task
        self.threads = self._resolve_thread_count(threads)

    def _filter_tasks(
        self, tasks: DownloadTaskSchema | list[DownloadTaskSchema]
    ) -> list[DownloadTaskSchema]:
        if isinstance(tasks, dict):
            tasks = [tasks]
        return tasks

    def _resolve_thread_count(self, threads: int | Literal["max"]) -> int:
        if threads == "max":
            return os.cpu_count() or 8
        if threads < 1:
            return 1
        return int(threads)

    def _download_task(self, task: DownloadTaskSchema):
        if task.get("query") and task.get("title"):
            yt_type = task.get("type", "default")
            if yt_type not in ("audio", "video", "default"):
                yt_type = "default"
            YTDownloader(
                query=task.get("query", ""),
                title=task.get("title", ""),
                type=yt_type,
                album=task.get("album", ""),
                playlist=task.get("playlist", "."),
                art=task.get("art", ""),
                artist=task.get("artist", ""),
                progress=self.progress,
            ).download()
        if self.progress is not None and self.playlist_task is not None:
            self.progress.playlist.update(
                self.playlist_task,
                advance=1,
            )

    def download(self):
        if not self.tasks:
            return
        if len(self.tasks) == 1:
            self._download_task(self.tasks[0])
            return

        threads: list[Thread] = []
        for task in self.tasks:
            t = Thread(target=self._download_task, args=(task,))
            t.start()
            threads.append(t)
            if len(threads) >= self.threads:
                threads[0].join()
                threads.pop(0)
        for t in threads:
            t.join()
