import datetime, time
import requests
from multidl import terminal
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, PictureType, TPE1
from yt_dlp import YoutubeDL
from pytube import Playlist
from youtubesearchpython import VideosSearch

class GetYTOptions:
    """
    Get yt-dlp options
    :param only_audio: download only audio
    :param dir: directory to save
    :param file_name: file name to save
    :param progress_hook: progress hook
    """
    def __init__(self, only_audio=False, dir="", file_name="", progress_hook=None):
        self.default_dir = "."
        self.default_file_name = "%(title)s"
        self.yt_options = None
        dir = dir if dir else self.default_dir
        file_name = file_name if file_name else self.default_file_name

        yt_options = {
            "quiet": True,
            "noprogress": True,
            "ignoreerrors": True,
            "format": "bv*+ba/best",
            "outtmpl": f"{dir}/{file_name}",
            "postprocessors": [],
        }
        if only_audio:
            yt_options["format"] = "ba[ext=m4a]/ba"
            yt_options["postprocessors"].append(
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "0"
                }
            )
        if progress_hook:
            yt_options["progress_hooks"] = [progress_hook]
        self.yt_options = yt_options

    def get(self):
        """
        Get options
        :rtype: dict
        """
        return dict(self.yt_options)

class AddMetaData:
    """
    Adds metadata to audio file
    :param file: file path
    :param art_url: album art url
    :param artist: artist name
    """
    def __init__(self, file, art_url, artist):
        art_data = requests.get(art_url).content
        if file.endswith(".mp3"):
            audio = MP3(file)
            audio.tags.add( # File icon
                APIC(
                    encoding=0,
                    mime="image/jpeg",
                    type=PictureType.FILE_ICON,
                    desc="Icon",
                    data=art_data
                )
            )
            audio.tags.add( # Song cover
                APIC(
                    encoding=0,
                    mime="image/jpeg",
                    type=PictureType.COVER_FRONT,
                    desc="Cover",
                    data=art_data
                )
            )
            audio["TPE1"] = TPE1(text=[artist if artist else "Unknown Artist"]) # Add artist
            audio.save(file)

class AdvanceSearchDL:
    def __init__(
            self, query: str = "",
            pl_name: str = "",
            only_audio: bool = False,
            title: str = "", thumbnail_url: str = "", artist: str = "",
            progress: terminal.MultiProgress = None
    ):
        """
        Advance search and download
        :param query: query
        :param list_query: list of queries
        :param pl_name: playlist name
        :param only_audio: download only audio
        :param title: title of the video/audio
        :param thumbnail_url: thumbnail url
        :param artist: artist
        :param progress: progress instance
        """
        self.progress = progress
        is_url = (query.startswith("http") or query.startswith("www")) and "youtube.com" in query
        # Progress
        _title = title if title.__len__() < 20 else title[:20].strip() + "..."
        task = self.progress.download.add_task(description=f"[yellow]Downloading[/] [cyan]{_title}[/]", total=0, start=False) # Progress
        # Info
        if not is_url:
            yt_options = GetYTOptions(query, only_audio, pl_name, title).get()
            with YoutubeDL(yt_options) as ytdlp:
                yt = ytdlp.extract_info(f"ytsearch:{query}", download=False)
        # Download
        def hook(d): # Progress hook
            self.progress.download.start_task(task) if "total_bytes" in d else None
            if d['status'] == "downloading":
                self.progress.download.update(task, total=d['total_bytes'] if "total_bytes" in d else d['downloaded_bytes']+1, completed=d['downloaded_bytes'])
            elif d['status'] == "finished":
                self.progress.download.update(task, description=f"[green]Downloaded[/] [cyan]{_title}[/]")
        yt_options = GetYTOptions(only_audio=only_audio, dir=pl_name, file_name=title, progress_hook=hook).get()
        with YoutubeDL(yt_options) as ytdlp:
            file_info = ytdlp.extract_info(yt['webpage_url'] if not is_url else query, download=True)
            file_entry = file_info['entries'][0] if "entries" in file_info else file_info
            AddMetaData(
                file_entry['requested_downloads'][0]['filepath'],
                thumbnail_url if thumbnail_url else file_entry['thumbnails'][0]['url'],
                artist if artist else file_entry['uploader']
            )
        self.progress.download.stop()

class YouTube:
    """
    Core downloader class
    :param query: url or search query
    """
    def __init__(self, query):
        self.query = query
        self.progress = terminal.MultiProgress()

    # Get playlist info
    def get_playlist_info(self):
        """Get playlist info"""
        with YoutubeDL({"quiet": True}) as ytdlp:
            with self.progress.live:
                # Progress
                task = self.progress.search.add_task("[yellow]Fetching Playlist Info[/]", total=1)
                # Info
                pl = ytdlp.extract_info(self.query, download=False, process=False)
                pl_data = [
                    ["Title", pl['title']],
                    ["Views", pl['view_count']],
                    ["Artist", pl['uploader']],
                    ["Modified Date", datetime.datetime.strptime(pl['modified_date'], "%Y%m%d").strftime("%d/%m/%Y")],
                    ["URL", pl['original_url']],
                    ["Thumbnail", pl['thumbnails'][0]['url']],
                    ["Videos", len([v for v in pl['entries']])],
                    ["Description", pl['description']],
                ]
                # Progress
                self.progress.search.update(task, description="[green]Fetched Playlist Info[/]", completed=1)
                time.sleep(1)
                self.progress.search.remove_task(task)
            # Print info
            terminal.InfoTable("Playlist", pl_data)

    # Get video info
    def get_video_info(self):
        """Get video info"""
        with YoutubeDL({"quiet": True}) as ytdlp:
            with self.progress.live:
                # Progress
                task = self.progress.search.add_task("[yellow]Fetching Video Info[/]", total=1)
                # Info
                video_info = ytdlp.extract_info(self.query, download=False)
                video_length = datetime.timedelta(seconds=video_info['duration'])
                video_data = [
                    ["Title", video_info['title']],
                    ["Length", video_length],
                    ["Views", video_info['view_count']],
                    ["Artist", video_info['uploader']],
                    ["URL", video_info['webpage_url']],
                    ["Thumbnail", video_info['thumbnails'][0]['url']],
                    ["Publish Date", datetime.datetime.strptime(video_info['upload_date'], "%Y%m%d").strftime("%d/%m/%Y")],
                    ["Description", video_info['description']]
                ]
                # Progress
                self.progress.search.update(task, description="[green]Fetched Video Info[/]", completed=1)
                time.sleep(1)
                self.progress.search.remove_task(task)
            # Print info
            terminal.InfoTable("Video", video_data)

    # Get search info
    def get_search_info(self):
        """Get search info"""
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Search Info[/]", total=1)
            # Info
            video_titles = []
            search = VideosSearch(self.query, limit=10).result()['result']
            for video in search:
                video_titles.append(video['title'])
            self.progress.search.update(task, description="[green]Fetched Search Info[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Ask info
        video_option = int(terminal.SearchTable(video_titles).get_option())
        video_url = search[video_option]['link']
        # Print info
        self.query = video_url
        self.get_video_info()

    # Download playlist
    def download_playlist(self, only_audio=False):
        """
        Download playlist
        :param only_audio: download only audio
        """
        yt_options = GetYTOptions(only_audio=only_audio).get()
        with YoutubeDL(yt_options) as ytdlp:
            with self.progress.live:
                # Progress
                task = self.progress.search.add_task("[yellow]Fetching Playlist[/]", total=1)
                # Info
                pl = Playlist(self.query)
                pl_title = pl.title # Fetching the playlist title here to ensure it is fetched during the progress
                # Progress to fetch playlist
                self.progress.search.update(task, description="[green]Fetched Playlist[/]", completed=1)
                time.sleep(1)
                self.progress.search.remove_task(task)
                # Progress for showing playlist data
                task = self.progress.playlist.add_task(f"[yellow]Downloading[/] [cyan]{pl_title}[/]", total=len(pl))
                # Download videos in playlist
                for video in pl.videos:
                    vid = ytdlp.extract_info(video.watch_url, download=False, process=False)
                    AdvanceSearchDL(
                        query=vid['webpage_url'],
                        only_audio=only_audio,
                        thumbnail_url=vid['thumbnails'][0]['url'],
                        artist=vid['uploader'],
                        pl_name=pl_title,
                        title=vid['title'],
                        progress=self.progress
                    )
                    # Progress for playlist data
                    self.progress.playlist.update(task, advance=1)
                # Progress finish for playlist data
                self.progress.playlist.update(task, description=f"[green]Downloaded[/] [cyan]{pl.title}[/]", completed=len(pl))

    # Download video
    def download_video(self, only_audio=False):
        """
        Download video
        :param only_audio: download only audio
        """
        with self.progress.live:
            # Info
            yt_options = GetYTOptions(only_audio=only_audio).get()
            with YoutubeDL(yt_options) as ytdlp:
                task = self.progress.search.add_task("[yellow]Fetching Video[/]", total=1) # Progress
                yt = ytdlp.extract_info(self.query, download=False)
                self.progress.search.update(task, description="[green]Fetched Video[/]", completed=1) # Progress update
                time.sleep(1)
                self.progress.search.remove_task(task) # Progress remove
            # Download
            AdvanceSearchDL(
                query=yt['webpage_url'],
                only_audio=only_audio,
                thumbnail_url=yt['thumbnails'][0]['url'],
                artist=yt['uploader'],
                title=yt['title'],
                progress=self.progress
            )

    # Download search
    def download_search(self, only_audio=False):
        """
        Download search
        :param only_audio: download only audio
        """
        with self.progress.live:
            # Progress
            task = self.progress.search.add_task("[yellow]Fetching Search[/]", total=1)
            # Info
            video_titles = []
            search = VideosSearch(self.query, limit=10).result()['result']
            for video in search:
                video_titles.append(video['title'])
            self.progress.search.update(task, description="[green]Fetched Search[/]", completed=1)
            time.sleep(1)
            self.progress.search.remove_task(task)
        # Ask and print info
        video_option = int(terminal.SearchTable(video_titles).get_option())
        video_url = search[video_option]['link']
        # Download
        self.query = video_url
        self.download_video(only_audio)
