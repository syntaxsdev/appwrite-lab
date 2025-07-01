import typer
from appwrite_lab.utils import console
from appwrite_lab.models import SyncType
from appwrite_lab import get_global_labs

sync_menu = typer.Typer(name="sync", help="Sync a resource to the lab.")


def sync_lab(
    name: str = typer.Argument(..., help="The name of the lab to sync."),
    appwrite_json: str = typer.Option(
        "appwrite.json", help="The appwrite.json file to sync."
    ),
    resource: SyncType = typer.Option(
        SyncType.ALL, show_default=True, help="The resource to sync."
    ),
):
    """
    Sync a resource to the lab.

    Args:
        name: The name of the lab to sync.
        resource: The resource to sync.
    """
    labs = get_global_labs()
    with console.status(f"Syncing lab '{name}'...", spinner="dots") as status:
        labs.sync_with_appwrite_config(
            name=name, appwrite_json=appwrite_json, sync_type=resource
        )
