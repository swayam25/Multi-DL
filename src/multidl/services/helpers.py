import os
from ..term import Print, ProgressBar
from ..utils import YTOptions
from dataclasses import dataclass
from rich.progress import TaskID
from threading import Thread
from typing import Literal, NotRequired, TypedDict
from yt_dlp import YoutubeDL


class YTDownloader:
    """
    Downloader class for downloading media. Uses yt-dlp to download media from YouTube.

    Parameters:
        query: The query string to be used for searching.
        title: The title of the media.
        type: The type of media to download.
        album: The album name of the media.
        playlist: The playlist folder name to save the media to.
        cover_url: The cover art URL to set.
        artist: The artist of the media.
        subtitles: List of subtitles to download.
        progress: A progress bar to use for downloading.
    """

    def __init__(
        self,
        query: str,
        title: str,
        type: Literal["audio", "video", "default"] = "default",
        album: str = "",
        playlist: str = ".",
        cover_url: str = "",
        artist: str = "",
        subtitles: list[str] | None = None,
        progress: ProgressBar | None = None,
    ):
        self.query = query
        self.type: Literal["audio", "video", "default"] = type
        self.album = album
        self.playlist = playlist
        self.cover_url = cover_url
        self.artist = artist
        self.subtitles = subtitles
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
        yt_opts = YTOptions(
            type=self.type,
            subtitles=self.subtitles,
            dir=self.playlist,
            filename=self.title,
            progress_hooks=[self.hook],
        ).get()
        with YoutubeDL(yt_opts) as ydl:
            yt = ydl.extract_info(
                # Checking url here adds support for non-YouTube URLs. Custom sources have dedicated downloaders.
                f"{'' if self.query.startswith('http://') or self.query.startswith('https://') else 'ytsearch:'}{self.query}"
                if not is_url
                else self.query
            )
        if not yt:
            Print.error(f"No results found for the query [cyan]{self.query}[/].")
            exit(1)
        file_entry = yt["entries"][0] if isinstance(yt, dict) and "entries" in yt else yt

        # Inject custom metadata
        artist = self.artist if self.artist else file_entry.get("uploader", "")
        album = (
            self.album
            if self.album
            else (file_entry.get("playlist", "") if file_entry.get("playlist") else "")
        )
        cover_url = (self.cover_url or file_entry.get("thumbnail")) or ""
        YTOptions.inject_metadata(dict(file_entry), self.title, artist or "", album, cover_url)

        ydl.process_info(file_entry)

    def hook(self, d):
        """Hook for yt-dlp to update the progress bar."""
        if self.progress is not None:
            total: int = (
                d["total_bytes"]
                if "total_bytes" in d
                else d.get("total_bytes_estimate", d["downloaded_bytes"])
            )
            if d["status"] == "downloading":
                self.progress.download.update(
                    self.task,
                    description=f"[yellow]Downloading[/] [cyan]{self._title}[/]",
                    total=total,
                    completed=d["downloaded_bytes"],
                )
            elif d["status"] == "finished":
                self.progress.download.update(
                    self.task,
                    description=f"[green]Downloaded[/] [cyan]{self._title}[/]",
                    total=total,
                    completed=total,
                )
                self.progress.download.refresh()
                self.progress.download.stop_task(self.task)


@dataclass
class DownloadTaskSchema(TypedDict):
    query: str
    title: str
    type: NotRequired[str]
    album: NotRequired[str]
    playlist: NotRequired[str]
    cover_url: NotRequired[str]
    artist: NotRequired[str]
    subtitles: NotRequired[list[str] | None]


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
        Parameters:
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
                cover_url=task.get("cover_url", ""),
                artist=task.get("artist", ""),
                subtitles=task.get("subtitles", None),
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
