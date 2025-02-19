import re
import shutil
from .youtube import YouTube
from .spotify import Spotify
from .terminal import PrintMultiDLInfo
from rich.console import Console

console = Console()

class MultiDL:
    """
    Core class for Multi DL
    :param query: Keyword or link to download or get info
    :type query: str
    """
    def __init__(self, query: str = ""):
        path = shutil.which("ffmpeg")
        if path is None:
            console.print("[red][bold]✗[/] FFmpeg is not installed[/]")
            console.print("Please install [link=https://ffmpeg.org/download.html bold cyan]FFmpeg[/] to use [cyan]multidl[/]")
            exit()
        self.query = query
        self.query = re.sub(
            r"(youtu\.be/|youtube\.com/shorts/|music\.youtube\.com/watch)",
            "youtube.com/watch?v=",
            self.query
        )
        self.query = self.query.split("&")[0]
        print()

    # Get info
    def get_info(self):
        """Get info about any multimedia via link, keywords etc"""
        yt = YouTube(self.query)
        if "youtube.com" in self.query:
            if "playlist" in self.query:
                yt.get_playlist_info()
            elif "watch" in self.query:
                yt.get_video_info()
        elif "open.spotify.com" in self.query:
            sp = Spotify(self.query)
            if "playlist" in self.query:
                sp.get_playlist_info()
            elif "album" in self.query:
                sp.get_album_info()
            elif "track" in self.query:
                sp.get_song_info()
        else:
            yt.get_search_info()

    # Download
    def download(self, only_audio: bool = False):
        """
        Download any multimedia via link, keywords etc.
        :param only_audio: Download only audio (only for youtube)
        """
        yt = YouTube(self.query)
        if "youtube.com" in self.query:
            if "playlist" in self.query:
                yt.download_playlist(only_audio)
            elif "watch" in self.query:
                yt.download_video(only_audio)
        elif "open.spotify.com" in self.query:
            sp = Spotify(self.query)
            if "playlist" in self.query:
                sp.download_playlist()
            elif "album" in self.query:
                sp.download_album()
            elif "track" in self.query:
                sp.download_song()
        else:
            yt.download_search(only_audio)

    # Init
    def init(self):
        """Initialize Multi DL"""
        self.query = console.input("[green]Enter a link or keyword:[/] ")
        option = console.input("[green]Do you want to download or get info? (d/i):[/] ")
        if option == "d":
            only_audio = console.input("[green]Do you want to download only audio? [cyan italic](only for youtube)[/] (y/n):[/] ")
            only_audio = True if only_audio == "y" else False
            self.download(only_audio)
        elif option == "i":
            self.get_info()
        else:
            console.print("[red][bold]✗[/] Invalid input[/]")

    # Package info
    def pkg_info(self):
        """Get info about Multi DL package"""
        PrintMultiDLInfo()
