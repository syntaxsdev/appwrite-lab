import typer
from appwrite_lab.utils import console
from appwrite_lab import get_global_labs

new_menu = typer.Typer(name="new", help="Create a new resource.")


@new_menu.command(name="lab", help="Create a new lab")
def new_lab(
    name: str = typer.Argument(..., help="The name of the lab to create."),
    version: str = typer.Option("1.7.4", help="The version of the lab to create."),
    port: int = typer.Option(80, help="The port to use for the Appwrite service."),
    email: str = typer.Option(
        None, help="The email to use for the admin account. Unset for random."
    ),
    password: str = typer.Option(
        None, help="The password to use for the admin account. Unset for random."
    ),
    project_id: str = typer.Option(
        None, help="The project ID to use for the lab. Unset for random."
    ),
    project_name: str = typer.Option(
        None, help="The name of the project to use for the lab. Unset for random."
    ),
):
    """
    Create a new lab.

    Args:
        name: The name of the lab to create.
        version: The version of the lab to create.
        port: The port to use for the Appwrite service. Must not be in use by another service.
        email: The email to use for the admin account. Unset for random.
        password: The password to use for the admin account. Unset for random.
        project_id: The project ID to use for the lab. Unset for random.
        project_name: The name of the project to use for the lab. Unset for random.
    """
    labs = get_global_labs()
    with console.status(f"Creating lab '{name}'...", spinner="dots") as status:
        creds = {
            "admin_email": email,
            "admin_password": password,
            "project_id": project_id,
            "project_name": project_name,
        }

        labs.new(name=name, version=version, port=port, meta={"appwrite_config": creds})
        status.update(f"Creating lab '{name}'... done")
