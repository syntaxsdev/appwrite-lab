from appwrite_lab import get_global_labs
from appwrite_lab.utils import print_table, console
from appwrite_lab._orchestrator import get_template_versions
import typer

list_menu = typer.Typer(name="list", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH)

labs = get_global_labs()


@list_menu.command(name="labs")
def get_labs():
    """List all ephemeral Appwrite instances."""
    pods = labs.orchestrator.get_labs()
    console.print(pods)
    # print_table(pods, ["Name", "Version", "Status"])

@list_menu.command()
def versions():
    """List all available Appwrite versions."""
    versions = get_template_versions()
    print_table(versions, ["Version"])
