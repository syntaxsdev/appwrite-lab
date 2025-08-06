from pathlib import Path

from appwrite_lab.labs import Labs
from appwrite_lab.models import Lab

import hashlib
import pytest


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
    hash_file_path = Path.home() / ".config" / "appwrite-lab" / "json_hashes"
    hash_file_path.touch()

    if lab := lab_svc.get_lab(lab_name):
        # Check if the file has changed before unnecessary sync
        if appwrite_file and appwrite_file.exists():
            hash = hash_file(appwrite_file)
            data = hash_file_path.read_text()
            if len(data) > 0 and data.strip() == hash:
                print("Skipping sync because the file has not changed")
            else:
                lab_svc.sync_with_appwrite_config(
                    name=lab_name, appwrite_json=appwrite_file
                )
                hash_file_path.write_text(hash)
        return lab

    res = lab_svc.new(**lab_config)

    if appwrite_file and appwrite_file.exists():
        hash_file_path.write_text(hash_file(appwrite_file))
        lab_svc.sync_with_appwrite_config(name=lab_name, appwrite_json=appwrite_file)

    if not res.error:
        return lab_svc.get_lab(lab_name)
    raise ValueError(res.message)


def hash_file(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
