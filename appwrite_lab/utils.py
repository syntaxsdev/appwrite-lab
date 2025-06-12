import os
import platform

from rich.console import Console
from rich.table import Table
from pathlib import Path

is_cli_setting: bool = False

console = Console()

APP_NAME = "appwrite-lab"


def ensure_dir():
    """Ensure APPWRITE directory exists."""
    os.makedirs(os.path.expanduser("~/.appwrite-lab"), exist_ok=True)
    return True


def print_table(data: list[list], headers: list[str]):
    """Print a 2D table of data.

    Args:
        data: A list of lists of data.
        headers: A list of headers.
    """
    console = Console()
    table = Table(style="purple")
    for header in headers:
        table.add_column(header, overflow="fold", style="purple")
    for row in data:
        table.add_row(*row)
    console.print(table)


def get_state_path():
    if platform.system() == "Windows":
        base = Path(os.getenv("APPDATA"))
    else:
        base = Path.home() / ".config"
    state_dir = base / APP_NAME
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "state.json"


def set_cli_true():
    global is_cli_setting
    is_cli_setting = True


@property
def is_cli():
    return is_cli_setting
