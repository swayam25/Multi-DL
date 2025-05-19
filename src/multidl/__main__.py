from . import __all__
from .config import Config
from .core import MultiDL
from .services.spotify import Credentials
from .term import ConfigPanel, MultiDLInfo, Print
from typer import Argument, Exit, Option, Typer
from typing import Literal

# Typer init
app = Typer(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


def version_callback(value: bool):
    """Version callback for Typer global option."""
    if value:
        MultiDLInfo(__all__).print()
        raise Exit()


@app.callback()
def main(
    version: bool = Option(
        None, "--version", "-v", callback=version_callback, is_eager=True, help="Shows version."
    ),
):
    pass


@app.command()
def version():
    """Shows Multi DL version."""
    MultiDLInfo(__all__).print()


@app.command()
def info(query: str = Argument(..., help="Keyword or link to get info")):
    """Get info about any media via link, keywords etc..."""
    MultiDL(query).info()


@app.command()
def download(
    query: str = Argument(..., help="Keyword or link to download"),
    audio: bool = Option(False, "--audio", "-a", help="Download only audio (only for youtube)."),
    video: bool = Option(False, "--video", "-v", help="Download only video (only for youtube)."),
    threads: str = Option(
        5,
        "--threads",
        "-t",
        help="Number of threads to use for downloading. Use 'max' for maximum threads..",
    ),
):
    """Download any media via link, keywords etc..."""
    threads = threads.lower()
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
        threads=_threads,
    )


@app.command()
def config(
    accept_spotify_tos: bool = Option(
        False,
        "--accept-spotify-tos",
        help="Accept Spotify TOS.",
    ),
    deny_spotify_tos: bool = Option(
        False,
        "--deny-spotify-tos",
        help="Deny Spotify TOS.",
    ),
    client_id: str = Option(
        None,
        "--client-id",
        "-i",
        help="Spotify client ID.",
    ),
    client_secret: str = Option(
        None,
        "--client-secret",
        "-s",
        help="Spotify client secret.",
    ),
    reset: bool = Option(
        False,
        "--reset",
        "-r",
        help="Reset Multi DL settings.",
    ),
    docs: bool = Option(False, "--docs", "-d", help="Get config docs."),
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


if __name__ == "__main__":
    app()
