import os
import shutil
import typer
from pathlib import Path
import subprocess
import json
from ._state import State
from dataclasses import dataclass
from .models import LabService
from dotenv import dotenv_values
from appwrite_lab.utils import console
from .utils import is_cli


@dataclass
class Response:
    message: str
    data: any
    error: bool = False

    def __post_init__(self):
        if is_cli:
            if self.error:
                console.print(self.message, style="red")
            else:
                console.print(self.message, style="green")


@dataclass
class CompletedProcess: ...


class OrchestratorError(Exception): ...


class ServiceOrchestrator:
    def __init__(self, state: State, backend: str = "auto"):
        self.backend = backend if backend != "auto" else detect_backend()
        self.state = state
        self.default_env_vars = str(
            Path(__file__).parent / "templates" / "environment" / "dotenv"
        )

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

    def get_running_pods_by_project(self, name: str):
        """
        Get the names of all running pods by project name.
        """
        cmd = [
            self.util,
            "ps",
            "--filter",
            f"label=com.docker.compose.project={name}",
            "--format",
            "json",
        ]
        result = run_cmd(cmd)
        pods = {
            pod["Names"]: pod
            for line in result.stdout.strip().splitlines()
            if line.strip()
            for pod in [json.loads(line)]
        }
        return pods

    def deploy_service(self, name: str, version: str, port: int):
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
                error=True, message=f"Lab '{name}' already deployed.", data=None
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

        # Override default env vars
        env_vars = get_env_vars(self.default_env_vars)
        if port != 80:
            env_vars["_APP_PORT"] = str(port)

        cmd = [self.compose, "-f", template_path, "-p", name, "up", "-d"]
        result = run_cmd(cmd, envs=env_vars)
        if result.returncode != 0:
            return Response(
                error=True, message=f"Failed to deploy lab {name}.", data=result.stdout
            )

        # Get appwrite pods
        project_pods = self.get_running_pods_by_project(name)
        if "appwrite" in project_pods:
            appwrite_pod = project_pods["appwrite"]
            port = appwrite_pod["Ports"]
            url = f"http://localhost:{port}"
        else:
            url = ""

        lab = LabService(name=name, version=version, url=url)
        return Response(
            error=False,
            message=f"Lab '{name}' deployed.",
            data=lab,
        )

    def check_pod_status(self, pod_name: str):
        """
        Check the status of a pod.
        """
        pods = self.get_running_pods()
        if pod_name not in pods:
            return False
        return True

    def wind_down_service(self, name: str):
        """
        Wind down a service.

        Args:
            name: The name of the service to wind down.
        """
        pods_by_project = self.get_pods_by_project(name)
        if not pods_by_project:
            return Response(
                error=True,
                message=f"Nothing to stop by name of '{name}'.",
                data=None,
            )
        cmd = [self.compose, "-p", name, "down"]
        result = run_cmd(cmd)
        return Response(
            message=f"Lab '{name}' stopped.",
            data=result.stdout,
        )

    def get_pods_by_project(self, project_name: str):
        """
        Get the names of all pods by project name.

        Args:
            project_name: The name of the project to get the pods for.
        """
        result = run_cmd(
            [
                self.util,
                "ps",
                "--filter",
                f"label=com.docker.compose.project={project_name}",
                "--format",
                "json",
            ]
        )
        return _stdout_to_json(result.stdout)

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


def run_cmd(cmd: list[str], envs: dict[str, str] | None = None):
    """Run a command and return the output.

    Args:
        cmd: The command to run.
        envs: The environment variables to set.
    """
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, **envs} if envs else None,
    )


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


def _stdout_to_json(stdout: str):
    """
    Convert stdout to a JSON object.

    Args:
        stdout: The stdout to convert to a JSON object.
    """
    return [json.loads(line) for line in stdout.strip().splitlines() if line.strip()]


def get_env_vars(name: str):
    """
    Get the default environment variables.
    """
    return dotenv_values(name)
