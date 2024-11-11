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
        self.query = query
        # Replace
        if "youtu.be/" in self.query:
            self.query = self.query.replace("youtu.be/", "youtube.com/watch?v=")
        elif "youtube.com/shorts/" in self.query:
            self.query = self.query.replace("youtube.com/shorts/", "youtube.com/watch?v=")
        elif "music.youtube.com/watch" in self.query:
            self.query = self.query.replace("music.youtube.com/watch", "youtube.com/watch")
        self.query = self.query.split("&")[0]
        print()

    # Get info
    def get_info(self):
        """Get info about any multimedia via link, keywords etc"""
        if "youtube.com" in self.query:
            if "playlist" in self.query:
                YouTube(self.query).get_playlist_info()
            elif "watch" in self.query:
                YouTube(self.query).get_video_info()
        elif "open.spotify.com" in self.query:
            if "playlist" in self.query:
                Spotify(self.query).get_playlist_info()
            elif "album" in self.query:
                Spotify(self.query).get_album_info()
            elif "track" in self.query:
                Spotify(self.query).get_song_info()
        else:
            YouTube(self.query).get_search_info()

    # Download
    def download(self, only_audio: bool = False):
        """
        Download any multimedia via link, keywords etc.
        :param only_audio: Download only audio (only for youtube)
        """
        if "youtube.com" in self.query:
            if "playlist" in self.query:
                YouTube(self.query).download_playlist(only_audio)
            elif "watch" in self.query:
                YouTube(self.query).download_video(only_audio)
        elif "open.spotify.com" in self.query:
            if "playlist" in self.query:
                Spotify(self.query).download_playlist()
            elif "album" in self.query:
                Spotify(self.query).download_album()
            elif "track" in self.query:
                Spotify(self.query).download_song()
        else:
            YouTube(self.query).download_search(only_audio)

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
