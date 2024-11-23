import datetime, time
import requests
import json
from typing import Literal
from .youtube import AdvanceSearchDL
from multidl import terminal

# Get temp spotify token
def get_spotify_token():
    sp = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player")
    return json.loads(sp.text)['accessToken']

class Spotify:
    """
    Spotify class
    :param url: spotify url
    :type url: str
    """
    def __init__(self, url):
        self.url = url
        self.sp_api = "https://api.spotify.com/v1"
        self.token = get_spotify_token()
        self.progress = terminal.MultiProgress()

    # Fetch raw data
    def fetch_raw(self, type: Literal["playlist", "album", "song"]):
        id = self.url.split(f"/{'track' if type == 'song' else type}/")[1]
        api = f"{self.sp_api}/tracks/{id}" if type == "song" else f"{self.sp_api}/{type}s/{id}"
        sp = requests.get(api, headers={"Authorization": f"Bearer {self.token}"})
        return sp.json()

    # Get info about playlist, album, song
    def get_info(self, type: Literal["playlist", "album", "song"], data: list):
        type = type.capitalize()
        with self.progress.live:
            task = self.progress.search.add_task(f"[yellow]Fetching {type} Info[/]", total=1)
            self.progress.search.update(task, description=f"[green]Fetched {type} Info[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Print info
        terminal.InfoTable(type, data)

    # Get playlist info
    def get_playlist_info(self):
        """Get playlist info"""
        pl = self.fetch_raw("playlist")
        pl_data = [
            ["Name", pl['name']],
            ["Owner", pl['owner']['display_name']],
            ["Followers", pl['followers']['total']],
            ["Public", pl['public']],
            ["Collaborative", pl['collaborative']],
            ["URL", pl['external_urls']['spotify']],
            ["Image", pl['images'][0]['url']],
            ["Tracks", pl['tracks']['total']],
            ["Description", pl['description']]
        ]
        self.get_info("playlist", pl_data)

    # Get album info
    def get_album_info(self):
        """Get album info"""
        album = self.fetch_raw("album")
        album_data = [
            ["Name", album['name']],
            ["Artist", album['artists'][0]['name']],
            ["Release Date", album['release_date']],
            ["URL", album['external_urls']['spotify']],
            ["Image", album['images'][0]['url']],
            ["Tracks", album['tracks']['total']],
        ]
        self.get_info("album", album_data)

    # Get song info
    def get_song_info(self):
        """Get song info"""
        song = self.fetch_raw("song")
        song_data = [
            ["Name", song['name']],
            ["Artist", song['artists'][0]['name']],
            ["Album", song['album']['name']],
            ["Release Date", song['album']['release_date']],
            ["URL", song['external_urls']['spotify']],
            ["Image", song['album']['images'][0]['url']],
            ["Duration", str(datetime.timedelta(milliseconds=song['duration_ms']))]
        ]
        self.get_info("song", song_data)

    # Download playlist
    def download_playlist(self):
        """Download playlist"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Playlist[/]", total=1)
            # Info
            pl = self.fetch_raw("playlist")
            # Progress
            self.progress.search.update(task, description="[green]Fetched Playlist[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            task = self.progress.playlist.add_task(f"[yellow]Downloading[/] [cyan]{pl['name']}[/]", total=pl['tracks']['total'])
            # Download
            for song in pl['tracks']['items']:
                # Download song
                AdvanceSearchDL(
                    query=song['track']['name'],
                    only_audio=True,
                    thumbnail_url=song['track']['album']['images'][0]['url'],
                    artist=song['track']['artists'][0]['name'],
                    pl_name=pl['name'],
                    title=f"{song['track']['name']}",
                    progress=self.progress
                )
                # Progress
                self.progress.playlist.update(task, advance=1)
            # Progress
            self.progress.playlist.update(task, description=f"[green]Downloaded[/] [cyan]{pl['name']}[/]", completed=pl['tracks']['total'])

    # Download album
    def download_album(self):
        """Download album"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Album[/]", total=1)
            # Info
            album = self.fetch_raw("album")
            # Progress
            self.progress.search.update(task, description="[green]Fetched Album[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            task = self.progress.playlist.add_task(f"[yellow]Downloading[/] [cyan]{album['name']}[/]", total=album['tracks']['total'])
            # Download
            for song in album['tracks']['items']:
                # Download
                AdvanceSearchDL(
                    query=song['name'],
                    only_audio=True,
                    thumbnail_url=album['images'][0]['url'],
                    artist=song['artists'][0]['name'],
                    pl_name=album['name'],
                    title=f"{song['name']}",
                    progress=self.progress
                )
                # Progress
                self.progress.playlist.update(task, advance=1)
            # Progress
            self.progress.playlist.update(task, description=f"[green]Downloaded[/] [cyan]{album['name']}[/]", completed=album['tracks']['total'])

    # download song
    def download_song(self):
        """Download song"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Song[/]", total=1)
            # Info
            song = self.fetch_raw("song")
            # Progress
            self.progress.search.update(task, description="[green]Fetched Song[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            # Download
            AdvanceSearchDL(
                query=song['name'],
                only_audio=True,
                thumbnail_url=song['album']['images'][0]['url'],
                artist=song['artists'][0]['name'],
                title=f"{song['name']}",
                progress=self.progress
            )