from appwrite_lab.models import Lab
from appwrite_lab.labs import Labs
from appwrite_lab.automations.models import Expiration
import pytest
import uuid

@pytest.mark.e2e
def test_labs_new(lab: Lab):
    assert lab.name == "test-lab"
    assert lab.version == "1.7.4"
    assert lab.url.endswith("80")
    assert lab.projects.get("default") is not None


@pytest.mark.e2e
def test_labs_create_api_key(lab: Lab, lab_svc: Labs):
    default = lab.projects.get("default")
    if default.api_key:
        pytest.skip("API key already exists")
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
def test_labs_synced_project(lab: Lab, lab_svc: Labs):
    synced_proj_name = "KubeProject"
    synced_proj = lab.projects.get(synced_proj_name)
    assert synced_proj is not None
    assert synced_proj.api_key.startswith("standard_")
    assert synced_proj.project_name == "KubeProject"


@pytest.mark.e2e
def test_labs_create_project(lab: Lab, lab_svc: Labs):
    nonce = str(uuid.uuid4())[:8]
    project_name = f"test-project-{nonce}"
    project_id = f"test-project-id-{nonce}"
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
