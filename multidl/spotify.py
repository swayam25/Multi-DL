import datetime, time
import requests
import json
from multidl.youtube import AdvanceSearchDL
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

    # Get playlist info
    def get_playlist_info(self):
        """Get playlist info"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Playlist Info[/]", total=1)
            # Info
            playlist_id = self.url.split("/playlist/")[1]
            sp = requests.get(f"{self.sp_api}/playlists/{playlist_id}", headers={"Authorization": f"Bearer {self.token}"})
            pl = sp.json()
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
            # Progress
            self.progress.search.update(task, description="[green]Fetched Playlist Info[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Print info
        terminal.InfoTable("Playlist", pl_data)

    # Get album info
    def get_album_info(self):
        """Get album info"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Album Info[/]", total=1)
            # Info
            album_id = self.url.split("/album/")[1]
            sp = requests.get(f"{self.sp_api}/albums/{album_id}", headers={"Authorization": f"Bearer {self.token}"})
            album = sp.json()
            album_data = [
                ["Name", album['name']],
                ["Artist", album['artists'][0]['name']],
                ["Release Date", album['release_date']],
                ["URL", album['external_urls']['spotify']],
                ["Image", album['images'][0]['url']],
                ["Tracks", album['tracks']['total']],
            ]
            # Progress
            self.progress.search.update(task, description="[green]Fetched Album Info[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Print info
        terminal.InfoTable("Album", album_data)

    # get song info
    def get_song_info(self):
        """Get song info"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Song Info[/]", total=1)
            # Info
            song_id = self.url.split("/track/")[1]
            sp = requests.get(f"{self.sp_api}/tracks/{song_id}", headers={"Authorization": f"Bearer {self.token}"})
            song = sp.json()
            song_data = [
                ["Name", song['name']],
                ["Artist", song['artists'][0]['name']],
                ["Album", song['album']['name']],
                ["Release Date", song['album']['release_date']],
                ["URL", song['external_urls']['spotify']],
                ["Image", song['album']['images'][0]['url']],
                ["Duration", str(datetime.timedelta(milliseconds=song['duration_ms']))]
            ]
            # Progress
            self.progress.search.update(task, description="[green]Fetched Song Info[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Print info
        terminal.InfoTable("Song", song_data)

    # Download playlist
    def download_playlist(self):
        """Download playlist"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Playlist[/]", total=1)
            # Info
            playlist_id = self.url.split("/playlist/")[1]
            sp = requests.get(f"{self.sp_api}/playlists/{playlist_id}", headers={"Authorization": f"Bearer {self.token}"})
            pl = sp.json()
            # Progress
            self.progress.search.update(task, description="[green]Fetched Playlist[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            task = self.progress.download.add_task(f"[yellow]Downloading[/] [cyan]{pl['name']}[/]", total=pl['tracks']['total'])
            # Download
            for song in pl['tracks']['items']:
                # Download song
                AdvanceSearchDL(
                    song['track']['name'],
                    True,
                    song['track']['album']['images'][0]['url'],
                    pl['name'],
                    f"{song['track']['name']} - {song['track']['artists'][0]['name']}"
                )
                # Progress
                self.progress.download.print(f"[green][bold]✓[/] Downloaded[/] [cyan]{song['track']['name']}[/]")
                self.progress.download.update(task, advance=1)
            # Progress
            self.progress.download.update(task, description=f"[green]Downloaded[/] [cyan]{pl['name']}[/]", completed=pl['tracks']['total'])

    # Download album
    def download_album(self):
        """Download album"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Album[/]", total=1)
            # Info
            album_id = self.url.split("/album/")[1]
            sp = requests.get(f"{self.sp_api}/albums/{album_id}", headers={"Authorization": f"Bearer {self.token}"})
            album = sp.json()
            # Progress
            self.progress.search.update(task, description="[green]Fetched Album[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            task = self.progress.download.add_task(f"[yellow]Downloading[/] [cyan]{album['name']}[/]", total=album['tracks']['total'])
            # Download
            for song in album['tracks']['items']:
                # Download
                AdvanceSearchDL(
                    song['track']['name'],
                    True,
                    song['track']['album']['images'][0]['url'],
                    album['name'],
                    f"{song['name']} - {song['artists'][0]['name']}"
                )
                # Progress
                self.progress.download.print(f"[green][bold]✓[/] Downloaded[/] [cyan]{song['name']}[/]")
                self.progress.download.update(task, advance=1)
            # Progress
            self.progress.search.update(task, description=f"[green]Downloaded[/] [cyan]{album['name']}[/]", completed=album['tracks']['total'])

    # download song
    def download_song(self):
        """Download song"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Song[/]", total=1)
            # Info
            song_id = self.url.split("/track/")[1]
            sp = requests.get(f"{self.sp_api}/tracks/{song_id}", headers={"Authorization": f"Bearer {self.token}"})
            song = sp.json()
            # Progress
            self.progress.search.update(task, description="[green]Fetched Song[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
            task = self.progress.download.add_task(f"[yellow]Downloading[/] [cyan]{song['name']}[/]", total=1)
            # Download
            AdvanceSearchDL(
                song['name'],
                True,
                song['album']['images'][0]['url'],
                "",
                f"{song['name']} - {song['artists'][0]['name']}"
            )
            # Progress
            self.progress.download.update(task, description=f"[green]Downloaded[/] [cyan]{song['name']}[/]", completed=1)