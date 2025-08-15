import pytest
from pathlib import Path
from appwrite_lab.models import Lab
from appwrite_lab.test_suite import lab_svc, appwrite_file, lab_config, lab
from appwrite_lab.tools.sms import SMS


@pytest.fixture(scope="session")
def appwrite_file_path():
    return Path(__file__).parent / "data" / "appwrite.json"


@pytest.fixture(scope="session")
def sms(lab: Lab):
    return SMS(lab)


@pytest.fixture(autouse=True)
async def clear_sms(sms: SMS):
    yield
    await sms.clear_messages()
