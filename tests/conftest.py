import pytest
from appwrite_lab.labs import Labs


@pytest.fixture(scope="session")
def lab_svc():
    return Labs()


@pytest.fixture(scope="session")
def lab(lab_svc: Labs):
    res = lab_svc.new(name="pytest-lab", version="1.7.4", port=8005)
    if not res.error:
        yield lab_svc.get_lab("pytest-lab")
        lab_svc.stop("pytest-lab")
    else:
        raise ValueError(res.message)
