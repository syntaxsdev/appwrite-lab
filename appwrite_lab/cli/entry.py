import typer
import typer.rich_utils
from appwrite_lab._orchestrator import ServiceOrchestrator, get_template_versions
from appwrite_lab._state import State
from appwrite_lab.utils import print_table

state = State()
# check backend preference
backend = state.get("backend")
if backend is None:
    backend = "docker"
    state.set("backend", backend)

orchestrator = ServiceOrchestrator(state)

app = typer.Typer(
    name="appwrite-lab", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH
)
list_app = typer.Typer(name="list", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH)


@app.command()
def new(
    name: str = typer.Option(..., help="The name of the ephemeral Appwrite instance."),
):
    """Spin up a new ephemeral Appwrite instance."""


@list_app.command()
def labs():
    """List all ephemeral Appwrite instances."""
    return orchestrator.get_running_pods()


@list_app.command()
def versions():
    """List all available Appwrite versions."""
    versions = get_template_versions()
    print_table(versions, ["Version"])


@app.command()
def delete(name: str):
    """Delete an ephemeral Appwrite instance."""


app.add_typer(list_app, name="list")
# @app.command()
# def
