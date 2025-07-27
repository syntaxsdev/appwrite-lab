from appwrite_lab.models import Lab
from appwrite_lab.labs import Labs
from appwrite_lab.automations.models import Expiration
import pytest


@pytest.mark.e2e
def test_labs_new(lab: Lab):
    assert lab.name == "test-lab"
    assert lab.version == "1.7.4"
    assert lab.url.endswith("8080")
    assert lab.projects.get("default") is not None


@pytest.mark.e2e
def test_labs_create_api_key(lab: Lab, lab_svc: Labs):
    default = lab.projects.get("default")
    res = lab_svc.create_api_key(
        project_name=default.project_name,
        key_name="default-api-key",
        expiration=Expiration.THIRTY_DAYS,
        lab=lab,
    )
    assert not res.error
    assert type(res.data) is str
    assert res.data.startswith("standard_")


@pytest.mark.e2e
def test_labs_create_project(lab: Lab, lab_svc: Labs):
    project_name = "test-project"
    project_id = "test-project-id"
    res = lab_svc.create_project(
        project_name=project_name,
        project_id=project_id,
        lab=lab,
    )
    assert not res.error

    res = lab_svc.create_api_key(
        project_name=project_name,
        key_name=project_name,
        expiration=Expiration.THIRTY_DAYS,
        lab=lab,
    )
    assert not res.error
    assert type(res.data) is str
    assert res.data.startswith("standard_")
