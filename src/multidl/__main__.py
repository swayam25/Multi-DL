from .config import Config
from .core import MultiDL
from .services.spotify import Credentials
from .term import ConfigPanel, MultiDLInfo, Print
from trogon.typer import init_tui
from typer import Argument, Exit, Option, Typer
from typing import Annotated, Literal

# Typer init
app = Typer(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool):
    """Version callback for Typer global option."""
    if value:
        MultiDLInfo().print()
        raise Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Shows version.",
        ),
    ] = False,
):
    pass


@app.command()
def version():
    """Shows Multi DL version."""
    MultiDLInfo().print()


@app.command()
def info(query: Annotated[str, Argument(..., help="Keyword or link to get info")]):
    """Get info about any media via link, keywords etc..."""
    MultiDL(query).info()


@app.command()
def download(
    query: Annotated[str, Argument(..., help="Keyword or link to download")],
    audio: Annotated[
        bool, Option("--audio", "-a", help="Download audio only (YouTube only).")
    ] = False,
    video: Annotated[
        bool, Option("--video", "-v", help="Download video only (YouTube only).")
    ] = False,
    subtitles: Annotated[
        list[str] | None,
        Option(
            "--subtitles",
            "-s",
            help="Subtitle languages to download for the video (YouTube only). Use 'all' to download all available subtitles.",
        ),
    ] = None,
    threads: Annotated[
        str,
        Option(
            "--threads",
            "-t",
            help="Number of threads to use for downloading. Use 'max' for maximum threads.",
        ),
    ] = "5",
):
    """Download any media via link, keywords etc..."""
    _threads: int | Literal["max"]
    if threads != "max" and not threads.isdigit():
        Print.error(
            "Invalid number of threads. Use 'max' for maximum threads or a positive integer."
        )
        exit(1)
    _threads = int(threads) if threads != "max" else "max"
    if isinstance(_threads, int) and int(threads) < 1:
        Print.error("Thread count must be at least 1. Using [cyan]1[/] thread instead.")
    MultiDL(query).download(
        type="audio" if audio else "video" if video else "default",
        subtitles=subtitles,
        threads=_threads,
    )


@app.command()
def config(
    accept_spotify_tos: Annotated[
        bool,
        Option(
            "--accept-spotify-tos",
            help="Accept Spotify TOS.",
        ),
    ] = False,
    deny_spotify_tos: Annotated[
        bool,
        Option(
            "--deny-spotify-tos",
            help="Deny Spotify TOS.",
        ),
    ] = False,
    client_id: Annotated[
        str | None,
        Option(
            "--client-id",
            "-i",
            help="Spotify client ID.",
        ),
    ] = None,
    client_secret: Annotated[
        str | None,
        Option(
            "--client-secret",
            "-s",
            help="Spotify client secret.",
        ),
    ] = None,
    reset: Annotated[
        bool,
        Option(
            "--reset",
            "-r",
            help="Reset Multi DL settings.",
        ),
    ] = False,
    docs: Annotated[
        bool,
        Option(
            "--docs",
            "-d",
            help="Get config docs.",
        ),
    ] = False,
):
    """Tweak Multi DL settings."""
    # Reset config
    if reset:
        Config().reset()
        Print.success("Successfully reset Multi DL settings.")
        exit(0)

    # Spotify TOS
    if accept_spotify_tos and deny_spotify_tos:
        Print.error("You cannot accept and deny Spotify TOS at the same time.")
        exit(1)
    if accept_spotify_tos:
        Config().accept_spotify_tos(True)
        Print.success("Accepted Spotify TOS.")
        exit(0)
    elif deny_spotify_tos:
        Config().accept_spotify_tos(False)
        Print.success("Denied Spotify TOS.")
        exit(0)

    # Spotify credentials
    if client_id and client_secret:
        if not Credentials(client_id, client_secret).verify():
            Print.error("Invalid Spotify credentials.")
            exit(1)
        Config().set_spotify_credentials(client_id, client_secret)
        Print.success("Successfully set Spotify credentials.")
        exit(0)
    elif client_id or client_secret:
        Print.error("Both [cyan]Client ID[/] and [cyan]Client secret[/] are required.")
        exit(1)

    # Config docs
    if docs:
        ConfigPanel.print_docs()
        exit(0)

    if not any([accept_spotify_tos, deny_spotify_tos, client_id, client_secret, docs]):
        perms = Print.confirm(
            "Config file may contain [yellow]sensitive[/] information. Do you want to see it"
        )
        if perms:
            ConfigPanel.print_config()
        else:
            Print.error("Permission denied.")


init_tui(app)

if __name__ == "__main__":
    app()
