import typer
from appwrite_lab.utils import console
from appwrite_lab import get_global_labs

# stop_menu = typer.Typer(name="stop", help="Teardown a lab resource.")


# @stop_menu.command(help="Stops a lab resource.")
def stop(name: str):
    """
    Stops a lab resource.

    Args:
        name: The name of the lab to stop.
    """
    labs = get_global_labs()
    with console.status(f"Stopping lab '{name}'...", spinner="dots") as status:
        labs.stop(name=name)
        status.update(f"Stopping lab '{name}'... done")
