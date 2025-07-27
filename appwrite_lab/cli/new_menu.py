import typer
from appwrite_lab.utils import console
from appwrite_lab import get_global_labs
from appwrite_lab.automations.models import Expiration

new_menu = typer.Typer(name="new", help="Create a new resource.")


@new_menu.command(name="lab", help="Create a new lab")
def new_lab(
    name: str = typer.Argument(..., help="The name of the lab to create."),
    version: str = typer.Option(
        "1.7.4", help="The version of the lab to create.", show_envvar=False
    ),
    port: int = typer.Option(
        80, help="The port to use for the Appwrite service.", show_envvar=False
    ),
    email: str = typer.Option(
        None,
        help="The email to use for the admin account. Unset for random.",
        show_envvar=False,
    ),
    password: str = typer.Option(
        None,
        help="The password to use for the admin account. Unset for random.",
        show_envvar=False,
    ),
    project_id: str = typer.Option(
        None,
        help="The project ID to use for the lab. Unset for random.",
        show_envvar=False,
    ),
    project_name: str = typer.Option(
        None,
        help="The name of the project to use for the lab. Unset for random.",
        show_envvar=False,
    ),
    just_deploy: bool = typer.Option(
        False,
        is_flag=True,
        help="Just deploy the lab without creating an API key or project.",
        show_envvar=False,
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
    extra_str = " with simple deployment" if just_deploy else ""
    with console.status(
        f"Creating lab '{name}'{extra_str}...", spinner="dots"
    ) as status:
        creds = {
            "admin_email": email,
            "admin_password": password,
            "project_id": project_id,
            "project_name": project_name,
        }

        labs.new(
            name=name,
            version=version,
            port=port,
            meta={"appwrite_config": creds},
            just_deploy=just_deploy,
        )
        status.update(f"Creating lab '{name}'... done")


@new_menu.command(name="api-key", help="Create a new API key")
def new_api_key(
    lab_name: str = typer.Argument(
        ..., help="The name of the lab to create the API key for."
    ),
    project_name: str = typer.Argument(
        ..., help="The name of the project to create the API key for."
    ),
    expiration: Expiration = typer.Option(
        Expiration.THIRTY_DAYS, help="The expiration of the API key.", show_envvar=False
    ),
):
    """
    Create a new API key.

    Args:
        lab_name: The name of the lab to create the API key for.
        project_name: The name of the project to create the API key for.
        expiration: The expiration of the API key.
    """
    with console.status(
        f"Creating API key for project '{project_name}'...", spinner="dots"
    ) as status:
        labs = get_global_labs()
        key = labs.create_api_key(
            project_name=project_name, lab_name=lab_name, expiration=expiration
        )
        status.update(f"Creating API key for project '{project_name}'... done")
        return key.data


@new_menu.command(name="project", help="Create a new project")
def new_project(
    lab_name: str = typer.Argument(
        ..., help="The name of the lab to create the project for."
    ),
    project_name: str = typer.Option(
        ...,
        help="The name to be assigned for the project.",
        show_envvar=False,
    ),
    project_id: str = typer.Option(
        ...,
        help="The ID to be assigned for the project.",
        show_envvar=False,
    ),
):
    """
    Create a new project.

    Args:
        lab_name: The name of the lab to create the project for.
        project_name: The name of the project to create.
        project_id: The ID of the project to create.
    """
    with console.status(f"Creating project '{project_name}'...", spinner="dots"):
        labs = get_global_labs()
        labs.create_project(
            project_name=project_name,
            project_id=project_id,
            lab_name=lab_name,
        )
