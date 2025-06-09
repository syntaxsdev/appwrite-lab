import typer
import typer.rich_utils

app = typer.Typer(name="appwrite-lab", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH)


@app.command()
def new(name: str = typer.Option(..., help="The name of the ephemeral Appwrite instance.")):
    """Spin up a new ephemeral Appwrite instance."""

@app.command()
def list():
    """List all ephemeral Appwrite instances."""

@app.command()
def delete(name: str):
    """Delete an ephemeral Appwrite instance."""
