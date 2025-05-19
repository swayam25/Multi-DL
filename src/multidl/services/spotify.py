import datetime
import requests
import spotipy
from ..config import Config
from ..term import InfoTable, Print, ProgressBar, SpotifyTOSTable
from .helpers import Downloader, DownloadTaskSchema
from typing import Literal


class Credentials:
    """
    Spotify credentials class for verifying credentials.

    Args:
        client_id: The Spotify client ID.
        client_secret: The Spotify client secret.
    """

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret

    def verify(self) -> bool:
        """Verify the Spotify credentials."""
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        if response.status_code != 200:
            return False
        return True

    @staticmethod
    def prompt() -> None:
        """Prompt the user for Spotify credentials."""
        client_id: str = Print.input("Enter your Spotify client ID", password=True)
        client_secret: str = Print.input("Enter your Spotify client secret", password=True)
        verified = Credentials(client_id, client_secret).verify()
        if not verified:
            Print.error("Invalid Spotify credentials.")
            exit(1)
        Config().set_spotify_credentials(client_id, client_secret)


class Spotify:
    """
    Spotify class for downloading media using spotify data.

    Args:
        query: The search query for the media.
    """

    def __init__(self, url: str):
        self.url = url
        self.progress = ProgressBar()

        config = Config()
        data = config.load()

        # Check if Spotify TOS is accepted
        if not data["spotify-tos"]:
            prompt = SpotifyTOSTable().ask()
            if not prompt:
                Print.error("You must accept the TOS to continue.")
                config.accept_spotify_tos(False)
                exit(1)
            config.accept_spotify_tos(True)
            Print.clear()

        # Check if Spotify credentials are set
        if any(
            [
                not data["spotify-credentials"],
                not data["spotify-credentials"]["client-id"],
                not data["spotify-credentials"]["client-secret"],
                data["spotify-credentials"]["client-id"] == "",
                data["spotify-credentials"]["client-secret"] == "",
            ]
        ):
            Print.error("Spotify credentials not found.")
            Credentials.prompt()
        elif not Credentials(
            data["spotify-credentials"]["client-id"],
            data["spotify-credentials"]["client-secret"],
        ).verify():
            Print.error("Invalid Spotify credentials.")
            Credentials.prompt()

        # Reload config
        data = config.load()

        # Initialize Spotify client
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.SpotifyClientCredentials(
                client_id=data["spotify-credentials"]["client-id"],
                client_secret=data["spotify-credentials"]["client-secret"],
                cache_handler=spotipy.cache_handler.MemoryCacheHandler(),
            )
        )

    def _fetch_info(self, fetch_fn, title: str):
        """Unified method to fetch Spotify info with progress bar and error handling."""
        with self.progress.live:
            task = self.progress.search.add_task(f"[yellow]Fetching {title}[/]", total=1)
            try:
                info = fetch_fn()
            except Exception:
                info = None
            if not info:
                self.progress.search.update(
                    task, description="[red][bold]✗[/] No Results Found[/]", completed=1
                )
                exit(1)
            self.progress.search.update(task, description=f"[green]Fetched {title}[/]", completed=1)
            self.progress.search.remove_task(task)
        return info

    def info_pl(self) -> None:
        """Get spotify playlist info."""
        pl = self._fetch_info(lambda: self.sp.playlist(self.url), "Spotify Playlist Info")
        data: list[tuple[str, str]] = [
            ("Name", pl["name"]),
            ("Owner", f"[link={pl['owner']['href']}]{pl['owner']['display_name']}[/]"),
            ("Followers", pl["followers"]["total"]),
            ("Public", pl["public"]),
            ("Collaborative", pl["collaborative"]),
            (
                "URL",
                f"[link={pl['external_urls']['spotify']}]{pl['external_urls']['spotify']}[/]",
            ),
            ("Image", f"[link={pl['images'][0]['url']}]{pl['images'][0]['url']}[/]"),
            ("Tracks", pl["tracks"]["total"]),
            ("Description", pl["description"]),
        ]
        InfoTable("Spotify Playlist", data).print()

    def info_album(self) -> None:
        """Get spotify album info."""
        album = self._fetch_info(lambda: self.sp.album(self.url), "Spotify Album Info")
        data: list[tuple[str, str]] = [
            ("Name", album["name"]),
            ("Artist", album["artists"][0]["name"]),
            ("Release Date", album["release_date"]),
            (
                "URL",
                f"[link={album['external_urls']['spotify']}]{album['external_urls']['spotify']}[/]",
            ),
            ("Image", f"[link={album['images'][0]['url']}]{album['images'][0]['url']}[/]"),
            ("Tracks", album["tracks"]["total"]),
        ]
        InfoTable("Spotify Album", data).print()

    def info_track(self) -> None:
        """Get spotify track info."""
        track = self._fetch_info(lambda: self.sp.track(self.url), "Spotify Track Info")
        data: list[tuple[str, str]] = [
            ("Name", track["name"]),
            ("Artist", track["artists"][0]["name"]),
            ("Album", track["album"]["name"]),
            ("Release Date", track["album"]["release_date"]),
            (
                "URL",
                f"[link={track['external_urls']['spotify']}]{track['external_urls']['spotify']}[/]",
            ),
            (
                "Image",
                f"[link={track['album']['images'][0]['url']}]{track['album']['images'][0]['url']}[/]",
            ),
            ("Duration", str(datetime.timedelta(milliseconds=track["duration_ms"]))),
        ]
        InfoTable("Spotify Track", data).print()

    def info_user(self) -> None:
        """Get spotify profile info."""
        user_id = self.url.split("/")[-1]
        user = self._fetch_info(lambda: self.sp.user(user_id), "Spotify Profile Info")
        data: list[tuple[str, str]] = [
            ("Name", user["display_name"]),
            ("Followers", user["followers"]["total"]),
            (
                "URL",
                f"[link={user['external_urls']['spotify']}]{user['external_urls']['spotify']}[/]",
            ),
            ("Image", f"[link={user['images'][0]['url']}]{user['images'][0]['url']}[/]"),
        ]
        InfoTable("Spotify Profile", data).print()

    def download_pl(self, threads: int | Literal["max"] = 5) -> None:
        """Download spotify playlist."""
        pl = self._fetch_info(lambda: self.sp.playlist(self.url), "Spotify Playlist")
        with self.progress.live:
            task = self.progress.playlist.add_task(
                f"[yellow]Downloading[/] [cyan]{pl['name']}[/]", total=pl["tracks"]["total"]
            )
            tasks = [
                DownloadTaskSchema(
                    query=track["track"]["name"],
                    title=track["track"]["name"],
                    type="audio",
                    art=track["track"]["album"]["images"][0]["url"],
                    artist=track["track"]["artists"][0]["name"],
                    album=track["track"]["album"]["name"],
                    playlist=pl["name"],
                )
                for track in pl["tracks"]["items"]
            ]
            Downloader(
                tasks=tasks,
                progress=self.progress,
                playlist_task=task,
                threads=threads,
            ).download()
            self.progress.playlist.update(
                task,
                description=f"[green]Downloaded[/] [cyan]{pl['name']}[/]",
                completed=pl["tracks"]["total"],
            )

    def download_album(self, threads: int | Literal["max"] = 5) -> None:
        """Download spotify album."""
        album = self._fetch_info(lambda: self.sp.album(self.url), "Spotify Album")
        with self.progress.live:
            task = self.progress.playlist.add_task(
                f"[yellow]Downloading[/] [cyan]{album['name']}[/]", total=album["tracks"]["total"]
            )
            tasks = [
                DownloadTaskSchema(
                    query=song["name"],
                    title=song["name"],
                    type="audio",
                    art=album["images"][0]["url"],
                    artist=song["artists"][0]["name"],
                    album=album["name"],
                    playlist=album["name"],
                )
                for song in album["tracks"]["items"]
            ]
            Downloader(
                tasks=tasks,
                progress=self.progress,
                playlist_task=task,
                threads=threads,
            ).download()
            self.progress.playlist.update(
                task,
                description=f"[green]Downloaded[/] [cyan]{album['name']}[/]",
                completed=album["tracks"]["total"],
            )

    def download_track(self, threads: int | Literal["max"] = 5) -> None:
        """Download spotify song."""
        song = self._fetch_info(lambda: self.sp.track(self.url), "Spotify Track")
        with self.progress.live:
            Downloader(
                tasks=[
                    DownloadTaskSchema(
                        query=song["name"],
                        title=song["name"],
                        type="audio",
                        art=song["album"]["images"][0]["url"],
                        artist=song["artists"][0]["name"],
                        album=song["album"]["name"],
                        playlist=song["album"]["name"],
                    )
                ],
                progress=self.progress,
                threads=threads,
            ).download()
