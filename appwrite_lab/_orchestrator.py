import os
import shutil
import typer
from pathlib import Path
import subprocess
import json
from ._state import State
from dataclasses import dataclass
from .models import LabService


@dataclass
class Response:
    message: str
    data: any
    error: bool = False


@dataclass
class CompletedProcess: ...


class OrchestratorError(Exception): ...


class ServiceOrchestrator:
    def __init__(self, state: State, backend: str = "auto"):
        self.backend = backend if backend != "auto" else detect_backend()
        self.state = state

    def get_running_pods(self):
        """
        Get the names of all running pods.
        """
        cmd = [self.util, "ps", "--format", "json"]
        result = run_cmd(cmd)
        pods = {
            pod["Names"]: pod
            for line in result.stdout.strip().splitlines()
            if line.strip()
            for pod in [json.loads(line)]
        }
        return pods

    def deploy_service(self, name: str, version: str):
        """
        Deploy a service.

        Args:
            name: The name to give to the deployment/project.
            version: The version of the service to deploy.
        """
        # sync
        pods_by_project = self.get_pods_by_project(name)
        if len(pods_by_project) > 0:
            return Response(
                error=True, message=f"Lab `{name}` already deployed.", data=None
            )
        converted_version = version.replace(".", "_")
        template_path = (
            Path(__file__).parent
            / "templates"
            / f"docker_compose_{converted_version}.yml"
        )
        if not template_path.exists():
            return Response(
                error=True, message=f"Template {version} not found.", data=None
            )
        cmd = [self.compose, "-f", template_path, "-p", name, "up", "-d"]
        result = run_cmd(cmd)
        if result.returncode != 0:
            return Response(
                error=True, message=f"Failed to deploy lab {name}.", data=result.stdout
            )
        return Response(
            error=False,
            message=f"Lab `{name}` deployed.",
            data=result.stdout,
        )

    def check_pod_status(self, pod_name: str):
        """
        Check the status of a pod.
        """
        pods = self.get_running_pods()
        if pod_name not in pods:
            return False
        return True

    def wind_down_service(self, service_name: str):
        """
        Wind down a service.

        Args:
            service_name: The name of the service to wind down.
        """
        services = self.state.get("services")
        if not self.check_pod_status(service_name):
            return Response(
                error=True, message=f"Service {service_name} is not running.", data=None
            )
        # cmd = [self.util, "compose", "down", service_name]

    def get_pods_by_project(self, project_name: str):
        """
        Get the names of all pods by project name.

        Args:
            project_name: The name of the project to get the pods for.
        """
        pods = run_cmd(
            [
                self.util,
                "ps",
                "--filter",
                f"label=com.docker.compose.project={project_name}",
                "--format",
                "json",
            ]
        )
        return pods

    @property
    def util(self):
        return shutil.which(self.backend)

    @property
    def compose(self):
        return shutil.which(f"{self.backend}-compose")


def detect_backend():
    if shutil.which("docker") and shutil.which("docker-compose"):
        return "docker"
    elif shutil.which("podman") and shutil.which("podman-compose"):
        return "podman"
    else:
        raise RuntimeError("Neither Docker nor Podman found.")


def run_cmd(cmd: list[str]):
    """Run a command and return the output.

    Args:
        cmd: The command to run.
    """
    return subprocess.run(cmd, capture_output=True, text=True)


def run_icmd(cmd: str):
    """
    Run a command and return the output.
    """
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def get_template_versions():
    """
    List all lab template versions available.
    """
    templates_dir = Path(__file__).parent / "templates"
    if templates_dir.exists():
        templates = [
            str(template.resolve()) for template in templates_dir.glob("*.yml")
        ]
    else:
        raise OrchestratorError(
            f"Templates directory not found: {templates_dir}. This should not happen."
        )

    versions = [
        template.split("/")[-1]
        .split(".")[0]
        .removeprefix("docker_compose_")
        .replace("_", ".")
        for template in templates
    ]
    return versions
