import typer
import typer.rich_utils
from appwrite_lab._orchestrator import ServiceOrchestrator, get_template_versions
from appwrite_lab._state import State
from appwrite_lab.utils import print_table, set_cli_true
from appwrite_lab import get_global_labs

from .new_menu import new_menu
from .stop_menu import stop

set_cli_true()

# Initialize the labs
labs = get_global_labs()
state = labs.state


app = typer.Typer(
    name="appwrite-lab", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH
)
list_app = typer.Typer(name="list", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH)


@list_app.command(name="labs")
def get_labs():
    """List all ephemeral Appwrite instances."""
    return labs.orchestrator.get_running_pods()


@list_app.command()
def versions():
    """List all available Appwrite versions."""
    versions = get_template_versions()
    print_table(versions, ["Version"])


@app.command()
def delete(name: str):
    """Delete an ephemeral Appwrite instance."""


app.add_typer(list_app, name="list")
app.add_typer(new_menu, name="new")
app.command()(stop)
# app.add_typer(stop_menu, name="stop")
