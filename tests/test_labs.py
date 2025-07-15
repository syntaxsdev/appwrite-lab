from appwrite_lab.models import Lab
from appwrite_lab.labs import Labs
from appwrite_lab.automations.models import Expiration
import pytest


def test_labs_new(lab: Lab):
    assert lab.name == "test-lab"
    assert lab.version == "1.7.4"
    assert lab.url.endswith("8080")
    assert lab.projects.get("default") is not None


def test_labs_create_api_key(lab: Lab, lab_svc: Labs):
    default = lab.projects.get("default")
    res = lab_svc.create_api_key(
        project_name=default.project_name,
        expiration=Expiration.THIRTY_DAYS,
        lab=lab,
    )
    assert res.data
