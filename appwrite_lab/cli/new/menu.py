import typer
from rich.spinner import Spinner

new_menu = typer.Typer(name="new", description="Create a new resource")


@new_menu.command(name="lab", help="Create a new lab")
def new_lab(name: str):
    """
    Create a new lab.
    
    Args:
        name: The name of the lab to create.
    """
    typer.secho(f"Creating lab `{name}`...", fg=typer.colors.GREEN)