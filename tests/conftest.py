import pytest
from pathlib import Path
from appwrite_lab.models import Lab
from appwrite_lab.test_suite import lab_svc, appwrite_file, lab_config, lab


@pytest.fixture(scope="session")
def appwrite_file_path():
    return Path(__file__).parent / "data" / "appwrite.json"
    