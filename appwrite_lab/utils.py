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


def print_table(data: list[dict], headers: list[str]):
    """Print a table of data."""
    console = Console()
    table = Table(*headers, style="purple")
    for row in data:
        table.add_row(row)
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
