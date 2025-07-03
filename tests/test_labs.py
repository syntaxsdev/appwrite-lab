from appwrite_lab.models import LabService


def test_labs_new(lab: LabService):
    assert lab.name == "pytest-lab"
