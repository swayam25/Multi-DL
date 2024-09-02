import datetime, time
import requests
from multidl import terminal
from mutagen.mp3 import MP3
from mutagen.id3 import APIC, PictureType
from mutagen.mp4 import MP4, MP4Cover
from yt_dlp import YoutubeDL
from youtubesearchpython import VideosSearch

class GetYTOptions:
    """
    Get yt-dlp options
    :param query: url or search query
    :param only_audio: download only audio
    :param dir: directory to save
    :param file_name: file name to sav
    :param playlist: is playlist
    """
    def __init__(self, query, only_audio=False, dir="", file_name="", playlist=False):
        if playlist:
            with YoutubeDL({"quiet": True}) as ytdlp:
                pl = ytdlp.extract_info(query, download=False)
                self.default_dir = pl['title']
        self.default_file_name = "%(title)s - %(channel)s"
        self.yt_options = None

        if playlist:
            dir = dir if dir else self.default_dir
        else:
            dir = dir if dir else "."
        file_name = file_name if file_name else self.default_file_name

        yt_options = {
            "quiet": True,
            "noprogress": True,
            "format": "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/b",
            "outtmpl": f"{dir}/{file_name}",
            "postprocessors": []
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
    """
    def __init__(self, file, art_url):
        art_data = requests.get(art_url).content
        if file.endswith(".mp4"):
            video = MP4(file)
            video["covr"] = [MP4Cover(art_data, imageformat=MP4Cover.FORMAT_JPEG)]
            video.save(file)
        elif file.endswith(".mp3"):
            audio = MP3(file)
            pic = APIC(
                encoding=0,
                mime="image/jpeg",
                type=PictureType.FILE_ICON,
                desc="File Icon",
                data=art_data
            )
            audio.tags.add(pic)
            audio.save(file)

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
        yt_options = GetYTOptions(query=self.query, only_audio=only_audio, playlist=True).get()
        with YoutubeDL(yt_options) as ytdlp:
            with self.progress.live:
                # Progress
                task = self.progress.search.add_task("[yellow]Fetching Playlist[/]", total=1)
                # Info
                pl = ytdlp.extract_info(self.query, download=False)
                # Progress
                self.progress.search.update(task, description="[green]Fetched Playlist[/]", completed=1)
                time.sleep(1)
                self.progress.search.remove_task(task)
                task = self.progress.download.add_task(f"[yellow]Downloading[/] [cyan]{pl['title']}[/]", total=len(pl['entries']))
                # Download
                for video in pl['entries']:
                    # Download
                    file_info = ytdlp.extract_info(video['webpage_url'], download=True)
                    # metadata
                    AddMetaData(file_info['requested_downloads'][0]['filepath'], video['thumbnails'][0]['url'])
                    # Progress
                    self.progress.download.print(f"[green][bold]✓[/] Downloaded[/] [cyan]{file_info['title']}[/]")
                    self.progress.update(task, advance=1)
                # Progress
                self.progress.download.update(task, description=f"[green]Downloaded[/] [cyan]{pl['title']}[/]", completed=len(pl['entries']))

    # Download video
    def download_video(self, only_audio=False):
        """
        Download video
        :param only_audio: download only audio
        """
        yt_options = GetYTOptions(query=self.query, only_audio=only_audio).get()
        with YoutubeDL(yt_options) as ytdlp:
            with self.progress.live:
                # Progress
                task = self.progress.search.add_task("[yellow]Fetching Video[/]", total=1)
                # Info
                yt = ytdlp.extract_info(self.query, download=False)
                # Progress
                self.progress.search.update(task, description="[green]Fetched Video[/]", completed=1)
                time.sleep(1)
                self.progress.search.remove_task(task)
                task = self.progress.download.add_task(f"[yellow]Downloading[/] [cyan]{yt['title']}[/]", total=1)
                # Download
                file_info = ytdlp.extract_info(yt['webpage_url'], download=True)
                # metadata
                AddMetaData(file_info['requested_downloads'][0]['filepath'], yt['thumbnails'][0]['url'])
                # Progress
                self.progress.download.update(task, description=f"[green]Downloaded[/] [cyan]{yt['title']}[/]", completed=1)

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
        self.download_video(only_audio=only_audio)

class AdvanceSearchDL:
    def __init__(self, query="", only_audio=False, thumbnail_url="", directory="", file_name=""):
        """
        Advance search and download
        :param query: query
        :param only_audio: download only audio
        :param thumbnail_url: thumbnail url
        :param directory: directory
        :param file_name: file name
        """
        yt_options = GetYTOptions(query, only_audio, directory, file_name).get()
        with YoutubeDL(yt_options) as ytdlp:
            # Info
            yt = ytdlp.extract_info(f"ytsearch:{query}", download=False)
            # Download
            file_info = ytdlp.extract_info(yt['webpage_url'], download=True)
            file_entry = file_info['entries'][0]
            # Metadata
            AddMetaData(file_entry['requested_downloads'][0]['filepath'], thumbnail_url if thumbnail_url else file_entry['thumbnails'][0]['url'])