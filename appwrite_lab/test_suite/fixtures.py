from pathlib import Path

import pytest
from appwrite_lab.labs import Labs
from appwrite_lab.models import Lab

@pytest.fixture(scope="session")
def lab_svc():
    """Lab service instance for managing Appwrite labs."""
    return Labs()


@pytest.fixture(scope="session")
def appwrite_file_path():
    """Override this fixture to specify appwrite.json location."""
    return NotImplementedError(
        "Override this fixture to specify appwrite.json location."
    )


@pytest.fixture(scope="session")
def appwrite_file(appwrite_file_path):
    if appwrite_file_path:
        file = Path(appwrite_file_path)
    else:
        # Look in current working directory
        file = Path.cwd() / "appwrite.json"

    if not file.exists():
        return None
    return file


@pytest.fixture(scope="session")
def lab_config():
    """Default lab configuration. Override in your test files."""
    return {"name": "test-lab", "version": "1.7.4", "port": 8080}


@pytest.fixture(scope="session")
def lab(lab_svc: Labs, appwrite_file: Path, lab_config: dict) -> Lab:
    """Create or get existing lab with optional appwrite.json sync."""
    lab_name = lab_config["name"]

    if lab := lab_svc.get_lab(lab_name):
        if appwrite_file and appwrite_file.exists():
            lab_svc.sync_with_appwrite_config(
                name=lab_name, appwrite_json=appwrite_file
            )
        return lab

    res = lab_svc.new(**lab_config)

    if appwrite_file and appwrite_file.exists():
        lab_svc.sync_with_appwrite_config(name=lab_name, appwrite_json=appwrite_file)

    if not res.error:
        return lab_svc.get_lab(lab_name)
    raise ValueError(res.message)
