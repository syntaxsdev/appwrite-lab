import os
import pytest
from appwrite_lab._orchestrator import ServiceOrchestrator, get_template_versions
from appwrite_lab._state import State
from tempfile import NamedTemporaryFile


@pytest.fixture()
def state(tmp_path):
    temp_file_path = tmp_path / "state.json"
    temp_file_path.write_text("{}")
    yield State(temp_file_path)
    temp_file_path.unlink(missing_ok=True)


@pytest.fixture
def orchestrator(state: State):
    return ServiceOrchestrator(state)


def test_orchestrator_init(orchestrator: ServiceOrchestrator):
    assert orchestrator.backend == "docker"
    assert orchestrator.util.endswith("docker")
    assert orchestrator.compose.endswith("docker-compose")


def test_get_templates():
    versions = get_template_versions()
    assert len(versions) > 0
    # assert all(template.endswith(".yml") for template in templates)


def test_check_pod_status(orchestrator: ServiceOrchestrator):
    running = orchestrator.check_pod_status("appwrite")
    print(running)


def test_deploy_service(orchestrator: ServiceOrchestrator):
    response = orchestrator.deploy_service("lab-1", "1.7.4")
    print("Res", response)
    assert response.message == "Lab `lab-1` deployed."
    assert response.data is None


# def test_wind_down_service(orchestrator: ServiceOrchestrator):
#     response = orchestrator.wind_down_service("appwrite")
