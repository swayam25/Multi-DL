import typer
from multidl.main import MultiDL

# Typer initialization
app = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    context_settings={
        "help_option_names": ["-h", "--help"]
    }
)

# Init
@app.command()
def init():
    """Interactive way for using Multi DL"""
    MultiDL().pkg_info()
    MultiDL().init()

# Info
@app.command()
def info(query: str = typer.Argument(..., help="Keyword or link to get info")):
    """Get info about any multimedia via link, keywords etc"""
    MultiDL(query).get_info()

# Download
@app.command()
def download(
    query: str = typer.Argument(..., help="Keyword or link to download"),
    only_audio: bool = typer.Option(False, "--only-audio", "-a", help="Download only audio (only for youtube)")
):
    """Download any multimedia via link, keywords etc"""
    MultiDL(query).download(only_audio)