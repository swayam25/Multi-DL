import datetime
from ..term import InfoTable, ProgressBar, SearchTable
from .helpers import Downloader, DownloadTaskSchema
from typing import Literal
from yt_dlp import YoutubeDL


def count_channel_entries(channel):
    """Count total entries (videos) in a channel object."""
    return sum(
        len(list(i["entries"])) if "entries" in i and i["entries"] else 1
        for i in channel["entries"]
    )


class Search:
    """
    Search videos from YouTube.

    Args:
        query: Query string to search for.
        progress: A progress bar to use for downloading.
    """

    def __init__(
        self,
        query: str,
        progress: ProgressBar,
    ):
        self.url: str | None = None

        with progress.live:
            task = progress.search.add_task("[yellow]Searching for videos[/]", total=1)
            self.vids: list[dict[str, str]] = []

            with YoutubeDL(
                {
                    "quiet": True,
                    "noprogress": True,
                    "ignoreerrors": True,
                    "format": "bv*+ba/best",
                    "extract_flat": True,
                    "noplaylist": True,
                }
            ) as ydl:
                info = ydl.extract_info(f"ytsearch20:{query}", download=False)
                if info and "entries" in info:  # Check if info is not None and has entries
                    for i in info["entries"]:
                        self.vids.append({"title": i["title"], "url": i["url"]})
                else:  # Throw an error if no entries are found and exit
                    progress.search.update(
                        task, description="[red][bold]✗[/] No Results Found[/]", completed=1
                    )
                    exit(1)
                progress.search.update(
                    task, description="[green]Fetched Search Info[/]", completed=1
                )
                progress.search.remove_task(task)
        self.video_url = self.vids[int(SearchTable(self.vids).get())]["url"]

    def get(self) -> str:
        """Get the selected video URL."""
        return self.video_url


class YouTube:
    """
    YouTube class for downloading media from YouTube.

    Args:
        query: The query string to be used for searching.
    """

    def __init__(self, query: str):
        self.query = query
        self.progress = ProgressBar()

    def _fetch_info(
        self,
        title: str,
        extract_flat: bool | Literal["in_playlist", "discard", "discard_in_playlist"] = False,
    ) -> dict:
        """Unified method to fetch info with progress bar and error handling."""
        ydl_opts = {"quiet": True, "noerrors": True, "extract_flat": extract_flat}
        with self.progress.live:
            task = self.progress.search.add_task(f"[yellow]Fetching {title}[/]", total=1)
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.query, download=False)
                if not info:
                    self.progress.search.update(
                        task, description="[red][bold]✗[/] No Results Found[/]", completed=1
                    )
                    exit(1)
                self.progress.search.update(
                    task,
                    description=f"[green]Fetched {title}[/]",
                    completed=1,
                )
                self.progress.search.remove_task(task)
        return info

    def info_pl(self) -> None:
        """Get the playlist info."""
        pl = self._fetch_info("Playlist Info", "in_playlist")
        pl_data: list[tuple[str, str]] = [
            ("Title", str(pl["title"])),
            ("Channel", str(pl["channel"])),
            ("Artist", str(pl["uploader"])),
            (
                "Modified Date",
                datetime.datetime.strptime(str(pl["modified_date"]), "%Y%m%d").strftime("%d/%m/%Y"),
            ),
            ("URL", f"[link={pl['original_url']}]{pl['original_url']}[/]"),
            (
                "Thumbnail",
                f"[link={pl['thumbnails'][0]['url']}]{pl['thumbnails'][0]['url']}[/]",
            ),
            ("Videos", str(len(list(pl["entries"])))),
            ("Description", str(pl["description"])),
        ]
        InfoTable("Playlist", pl_data).print()

    def info_video(self) -> None:
        """Get the video info."""
        video = self._fetch_info("Video Info", True)
        video_data: list[tuple[str, str]] = [
            ("Title", str(video["title"])),
            ("Length", str(datetime.timedelta(seconds=video["duration"]))),
            ("Views", str(video["view_count"])),
            ("Artist", str(video["uploader"])),
            ("URL", f"[link={video['webpage_url']}]{video['webpage_url']}[/]"),
            (
                "Thumbnail",
                f"[link={video['thumbnails'][0]['url']}]{video['thumbnails'][0]['url']}[/]",
            ),
            (
                "Publish Date",
                datetime.datetime.strptime(str(video["upload_date"]), "%Y%m%d").strftime(
                    "%d/%m/%Y"
                ),
            ),
            ("Description", str(video["description"])),
        ]
        InfoTable("Video", video_data).print()

    def info_channel(self) -> None:
        """Get the channel info."""
        channel = self._fetch_info("Channel Info", True)
        avatar_list = [i for i in channel["thumbnails"] if i["id"] == "avatar_uncropped"]
        avatar = avatar_list[0]["url"] if avatar_list else ""
        banner_list = [i for i in channel["thumbnails"] if i["id"] == "banner_uncropped"]
        banner = banner_list[0]["url"] if banner_list else ""
        channel_data: list[tuple[str, str]] = [
            ("Name", str(channel["channel"])),
            ("Subscribers", str(channel["channel_follower_count"])),
            (
                "Videos",
                str(count_channel_entries(channel)),
            ),
            ("URL", str(f"[link={channel['webpage_url']}]{channel['webpage_url']}[/]")),
            (
                "Avatar",
                str(f"[link={avatar}]{avatar}[/]"),
            ),
            (
                "Banner",
                str(f"[link={banner}]{banner}[/]"),
            ),
            ("Tags", str(", ".join(list(channel["tags"])))),
            ("About", str(channel["description"])),
        ]
        InfoTable("Channel", channel_data).print()

    def info_search(self) -> None:
        """Get search info."""
        self.query = Search(self.query, self.progress).get()
        self.info_video()

    def download_pl(
        self,
        type: Literal["audio", "video", "default"] = "default",
        threads: int | Literal["max"] = 5,
    ) -> None:
        """
        Download the playlist.

        Args:
            type: The type of media to download.
        """
        pl = self._fetch_info("Playlist", "in_playlist")
        with self.progress.live:
            task = self.progress.playlist.add_task(
                f"[yellow]Downloading Playlist[/] [cyan]{pl['title']}[/]",
                total=len(pl["entries"]),
            )
            tasks = [
                DownloadTaskSchema(
                    query=i["url"],
                    title=i["title"],
                    type=type,
                    album=pl["title"],
                    playlist=pl["title"],
                )
                for i in pl["entries"]
            ]
            Downloader(
                tasks=tasks,
                progress=self.progress,
                playlist_task=task,
                threads=threads,
            ).download()
            self.progress.playlist.update(
                task,
                description=f"[green]Downloaded Playlist[/] [cyan]{pl['title']}[/]",
                completed=len(pl["entries"]),
            )

    def download_video(
        self,
        type: Literal["audio", "video", "default"] = "default",
        threads: int | Literal["max"] = 5,
    ) -> None:
        """
        Download the video.

        Args:
            type: The type of media to download.
        """
        vid = self._fetch_info("Video", True)
        with self.progress.live:
            tasks = [
                DownloadTaskSchema(
                    query=self.query,
                    title=vid["title"],
                    type=type,
                )
            ]
            Downloader(
                tasks=tasks,
                progress=self.progress,
                threads=threads,
            ).download()

    def download_channel(
        self,
        type: Literal["audio", "video", "default"] = "default",
        threads: int | Literal["max"] = 5,
    ) -> None:
        """
        Download the channel.

        Args:
            type: The type of media to download.
        """
        channel = self._fetch_info("Channel", True)
        with self.progress.live:
            task = self.progress.playlist.add_task(
                f"[yellow]Downloading Channel[/] [cyan]{channel['channel']}[/]",
                total=count_channel_entries(channel),
            )
            tasks = []
            for i in channel["entries"]:
                if i["entries"]:
                    for j in i["entries"]:
                        tasks.append(
                            DownloadTaskSchema(
                                query=j["url"],
                                title=j["title"],
                                type=type,
                                album=channel["channel"],
                                playlist=f"{channel['channel']}%dir%{i['title']}",
                            )
                        )
                else:
                    tasks.append(
                        DownloadTaskSchema(
                            query=i["url"],
                            title=i["title"],
                            type=type,
                            album=channel["channel"],
                            playlist=channel["channel"],
                        )
                    )
            Downloader(
                tasks=tasks,
                progress=self.progress,
                playlist_task=task,
                threads=threads,
            ).download()
            self.progress.playlist.update(
                task,
                description=f"[green]Downloaded Channel[/] [cyan]{channel['channel']}[/]",
                completed=count_channel_entries(channel),
            )

    def download_search(
        self,
        type: Literal["audio", "video", "default"] = "default",
        threads: int | Literal["max"] = 5,
    ) -> None:
        """
        Download the search result.

        Args:
            type: The type of media to download.
        """
        self.query = Search(self.query, self.progress).get()
        self.download_video(type, threads)
