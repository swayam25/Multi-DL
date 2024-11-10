from rich import print, box
from rich.console import Console, Group
from rich.live import Live
from rich.progress import *
from rich.panel import Panel
from rich.table import Table

# Rich's console initialization
console = Console()

# UI class
class InfoTable(Table):
    """
    Info Table Printing Util
    :param info_type: Type of info to be printed
    :param data: Data to be printed
    """
    def __init__(self, info_type: str, data: list):
        super().__init__(box=None)
        # Data arranger
        for data in data:
            self.add_row(
                f"[yellow]•[/] [green bold]{data[0]}[/]",
                f"[cyan]{data[1]}[/]"
            )
        # Panel
        panel = Panel.fit(self, box=box.ROUNDED, title=f"[green bold]{info_type} Info[/]", style="green")
        # Print
        print(panel)

class SearchTable(Table):
    """
    Search Table Printing Util
    :param titles: Titles to be printed
    """
    def __init__(self, titles: list):
        super().__init__(box=None)
        self.option = 1
        options = ""
        # Data arranger
        for index in range(10):
            options += f"[white][[cyan]{index}[/]][/] [green]{titles[index]}[/]\n"
        options = options[:-1]
        # Panel
        panel = Panel.fit(
            title="[bold green]Top 10 Search Results[/]",
            renderable=options,
            padding=1,
            box=box.ROUNDED,
            style="green"
        )
        # Print
        print(panel)
        # Ask
        self.option = console.input("[green]Enter the option number:[/] ")

    def get_option(self):
        return self.option

class PrintMultiDLInfo:
    """MultiDL Info Printing Util"""
    def __init__(self):
        console.print(
            r"[green]  /##      /##           /##   /##     /##       /#######  /##      [/]" + "\n" +
            r"[green] | ###    /###          | ##  | ##    |__/      | ##__  ##| ##      [/]" + "\n" +
            r"[green] | ####  /#### /##   /##| ## /######   /##      | ##  \ ##| ##      [/]" + "\n" +
            r"[green] | ## ##/## ##| ##  | ##| ##|_  ##_/  | ##      | ##  | ##| ##      [/]" + "\n" +
            r"[red] | ##  ###| ##| ##  | ##| ##  | ##    | ##      | ##  | ##| ##      [/]" + "\n" +
            r"[red] | ##\  # | ##| ##  | ##| ##  | ## /##| ##      | ##  | ##| ##      [/]" + "\n" +
            r"[red]      | ## \/  | ##|  ######/| ##  |  ####/| ##      | #######/| ########[/]" + "\n" +
            r"[red]      |__/     |__/ \______/ |__/   \___/  |__/      |_______/ |________/[/]", justify="center"
        )

class MultiProgress:
    """Multi Progress Bar Printing Util"""
    download = Progress(
        SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        DownloadColumn(),
        TextColumn("•"),
        TransferSpeedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(compact=True)
    )
    playlist = Progress(
        SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn()
    )
    search = Progress(
        SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
        TextColumn("[progress.description]{task.description}")
    )
    live = Live(Group(download, playlist, search))
