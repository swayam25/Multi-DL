from .config import DEFAULT_CONFIG_PATH, MULTIDL_CONFIG, Config
from dataclasses import dataclass
from importlib.metadata import metadata
from pyfiglet import Figlet
from rich import box
from rich.console import Console, Group
from rich.live import Live
from rich.padding import Padding
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    DownloadColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table

console = Console()


class InfoTable(Table):
    """
    Generate rich info table.

    Args:
        info_type: Type of info to be printed.
        data: Data to be printed.
    """

    def __init__(self, info_type: str, data: list[tuple[str, str]]):
        super().__init__(box=None, show_header=False)
        for i in data:
            self.add_row(f"[yellow bold]•[/] [green bold]{i[0]}[/]", f"[cyan]{i[1]}[/]")
        self.panel = Panel.fit(
            self,
            title=f"[green bold]{info_type} Info[/]",
            title_align="left",
            style="green",
            padding=1,
            box=box.ROUNDED,
        )

    def print(self) -> None:
        """Print the info table."""
        console.print(self.panel)


class SearchTable(Table):
    """
    Generate rich search table.

    Args:
        data: List of video dictionaries containing 'url' and 'title'.
    """

    def __init__(self, data: list[dict[str, str]]):
        super().__init__(box=None, show_header=False)
        self.option: int = 1
        for idx, i in enumerate(data, start=1):
            self.add_row(f"[white][[cyan]{idx}[/]][/]", f"[green]{i['title']}[/]")
        panel = Panel.fit(
            self,
            title=f"[bold green]Top {len(data)} Search Results[/]",
            title_align="left",
            style="green",
            padding=1,
            box=box.ROUNDED,
        )
        console.print(panel)
        self.option = int(
            Print.input(
                f"Enter the option number [[cyan]1-{len(data) + 1}[/]]",
                choices=[str(i) for i in range(1, len(data) + 1)],
            )
        )

    def get(self):
        return self.option - 1


class SpotifyTOSTable(Panel):
    """Generate Spotify TOS confirmation table."""

    def __init__(self):
        super().__init__(
            title="[bold yellow]Terms of Service[/]",
            renderable="\n".join(
                [
                    "[red][bold]![/] You must agree to the [link=https://www.spotify.com/legal/end-user-agreement cyan]Spotify TOS[/] to use this feature.[/]",
                    "[bold]•[/] Multi DL does not collect or store any user data. Your playlist, song, or related information is only used temporarily to retrieve and display content, and is never used for personal or commercial purposes.",
                    "[bold]•[/] Do not use this application for illegal activities or in any way that violates Spotify's [link=https://developer.spotify.com/terms cyan]Developer Terms of Service[/].",
                    "[bold]•[/] You must not use MultiDL to sell, distribute, or misuse any data obtained through this tool.",
                ]
            ),
            style="yellow",
            title_align="left",
            padding=1,
            box=box.ROUNDED,
        )
        console.print(self)

    def ask(self) -> bool:
        """Ask the user to confirm if they agree to the TOS."""
        return Print.confirm(
            "Do you agree to the [link=https://www.spotify.com/legal/end-user-agreement cyan]Spotify TOS[/]"
        )


class ConfigPanel:
    """
    Generate config panel.

    Args:
        file_path: Path to the config file.
    """

    @staticmethod
    def print_config() -> None:
        """Print the config panel."""
        Config()
        panel = Panel(
            Syntax.from_path(
                MULTIDL_CONFIG,
                word_wrap=True,
                line_numbers=True,
                theme="ansi_dark",
                indent_guides=True,
            ),
            title="[bold green]Multi DL Config[/]",
            subtitle=f"[green]Config file path: [bold cyan]{MULTIDL_CONFIG}[/]",
            style="green",
            title_align="left",
            padding=1,
            box=box.ROUNDED,
        )
        console.print(panel)

    @staticmethod
    def print_docs() -> None:
        """Print the config panel documentation."""
        panel = Panel(
            Group(
                "[bold yellow]How to set multidl config file path?[/]",
                Padding(
                    "\n".join(
                        [
                            "[white]Config file path can be overridden by setting the [cyan]MULTIDL_CONFIG[/] environment variable.[/]",
                            f"[white]Default path is set to [cyan]{DEFAULT_CONFIG_PATH}[/].",
                            f"[yellow]Current config file path: [cyan]{MULTIDL_CONFIG}[/]\n",
                        ]
                    ),
                    (0, 0, 0, 2),
                ),
                "[bold yellow]How to set Spotify credentials?[/]",
                Padding(
                    "\n".join(
                        [
                            "[white]You can set Spotify credentials via both the config file and commands.[/]",
                            "[white]It can be set using [cyan]multidl config -i <client_id> -s <client_secret>[/] command.[/]",
                            "[white][cyan]Client ID[/] and [cyan]Client Secret[/] can be obtained from the [link=https://developer.spotify.com/dashboard/applications cyan]Spotify Developer Dashboard[/]. Refer to the [link=https://developer.spotify.com/documentation/general/guides/app-settings/ cyan]Spotify App Settings[/] for more information.[/]",
                        ]
                    ),
                    (0, 0, 0, 2),
                ),
            ),
            title="[bold yellow]Config Docs[/]",
            style="yellow",
            title_align="left",
            padding=1,
            box=box.ROUNDED,
        )
        console.print(panel)


@dataclass
class ProgressBar:
    """Multiple progress bars for multidl."""

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
        TimeRemainingColumn(compact=True),
    )
    playlist = Progress(
        SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
    )
    search = Progress(
        SpinnerColumn(style="yellow", finished_text="[green bold]✓[/]"),
        TextColumn("[progress.description]{task.description}"),
    )
    live = Live(Group(download, playlist, search))


class MultiDLArt:
    """ASCII art for Multi DL."""

    def __init__(self):
        txt = Figlet(font="big_money-ne", justify="center").renderText("Multi DL")
        txt = txt.replace("$", "#")
        lines = txt.splitlines()
        green_part = "\n".join(f"[green]{line}[/]" for line in lines[: len(lines) // 2])
        red_part = "\n".join(f"[red]{line}[/]" for line in lines[len(lines) // 2 :])
        self.ascii = green_part + "\n" + red_part

    def get(self) -> str:
        """Get the Multi DL ASCII art."""
        return self.ascii


class MultiDLInfo(Panel):
    """Multi DL info."""

    def __init__(self, supported_services: list[str]):
        data = metadata("multidl")
        info = {
            "Version": data.get("Version"),
            "Description": data.get("Summary"),
            "License": data.get("License-Expression"),
            "Supported Services": ", ".join(supported_services),
        }
        self.art = MultiDLArt().get()
        self.table = Table(box=None, show_header=False)
        for i in info:
            self.table.add_row(f"[yellow bold]•[/] [green bold]{i}[/]", f"[white]{info[i]}[/]")
        super().__init__(
            Group(self.art, self.table),
            title=f"[green bold]Multi DL v{info['Version']}[/]",
            subtitle="[green]Made with ❤️  by [link=https://github.com/swayam25 bold cyan]Swayam[/]",
            box=box.ROUNDED,
            title_align="left",
            style="green",
            expand=False,
            padding=1,
        )

    def print(self) -> None:
        """Print the Multi DL info."""
        console.print(self)


class Print:
    """Print class for colored messages."""

    @staticmethod
    def input(data: str, choices: list[str] | None = None, password: bool = False) -> str:
        """
        Print an input message and return the user input.

        Args:
            data: The message to print.
            choices: List of choices for the prompt. Defaults to None.
            password: If True, input will be masked. Defaults to False.
        """
        return Prompt.ask(
            f"[green bold]?[/] [bold]{data}[/]",
            show_default=False,
            choices=choices,
            show_choices=False,
            password=password,
        )

    @staticmethod
    def confirm(data: str) -> bool:
        """
        Print a confirmation message and return the user's choice.

        Args:
            data: The message to print.
        """
        return Confirm.ask(
            f"[green bold]?[/] [bold]{data}[/]",
            default=False,
            show_default=False,
        )

    @staticmethod
    def error(data: str) -> None:
        """
        Print an error message.

        Args:
            data: The error message to print.
        """
        console.print(f"[red][bold]✗[/] {data}[/]")

    @staticmethod
    def success(data: str) -> None:
        """
        Print a success message.

        Args:
            data: The success message to print.
        """
        console.print(f"[green][bold]✓[/] {data}[/]")

    @staticmethod
    def warn(data: str) -> None:
        """
        Print a warning message.

        Args:
            data: The warning message to print.
        """
        console.print(f"[yellow][bold]![/] {data}[/]")

    @staticmethod
    def clear() -> None:
        """Clear the console."""
        console.clear()
