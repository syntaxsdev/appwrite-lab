import typer
from appwrite_lab.utils import console
from appwrite_lab import get_global_labs

new_menu = typer.Typer(name="new", help="Create a new resource.")


@new_menu.command(name="lab", help="Create a new lab")
def new_lab(
    name: str = typer.Option(..., help="The name of the lab to create."),
    version: str = typer.Option("1.7.4", help="The version of the lab to create."),
):
    """
    Create a new lab.

    Args:
        name: The name of the lab to create.
    """
    labs = get_global_labs()
    with console.status(f"Creating lab `{name}`...", spinner="dots") as status:
        labs.new(name=name, version=version)
        status.update(f"Creating lab `{name}`... done")
