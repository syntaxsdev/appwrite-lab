import typer
from appwrite_lab.utils import set_cli_true
from appwrite_lab import get_global_labs

from .new_menu import new_menu
from .list_menu import list_menu
from .stop_menu import stop

set_cli_true()

# Initialize the labs
labs = get_global_labs()
state = labs.state


app = typer.Typer(
    name="appwrite-lab", rich_markup_mode=typer.rich_utils.MARKUP_MODE_RICH
)


app.add_typer(list_menu, name="list")
app.add_typer(new_menu, name="new")
app.command()(stop)
# app.add_typer(stop_menu, name="stop")
