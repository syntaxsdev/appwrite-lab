from appwrite_lab import get_global_labs
from appwrite_lab.utils import print_table
from appwrite_lab._orchestrator import get_template_versions
import typer

try:
    from typer.rich_utils import MARKUP_MODE_RICH

    RICH_MODE = MARKUP_MODE_RICH
except Exception:
    RICH_MODE = "rich"

list_menu = typer.Typer(name="list", rich_markup_mode=RICH_MODE)

labs = get_global_labs()


@list_menu.command(name="labs", help="List resources.")
def get_labs():
    """List all ephemeral Appwrite instances."""
    headers, pods = labs.orchestrator.get_formatted_labs(collapsed=True)
    print_table(pods, headers)


@list_menu.command()
def versions():
    """List all available Appwrite versions."""
    versions = get_template_versions()
    print_table([versions], ["Version"])
