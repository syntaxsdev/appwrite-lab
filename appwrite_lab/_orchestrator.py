import os
import shutil
import subprocess
import json
import tempfile
from pathlib import Path

from appwrite_lab.automations.models import BaseVarModel
from ._state import State
from dataclasses import dataclass
from .models import LabService, Automation, SyncType
from dotenv import dotenv_values
from appwrite_lab.utils import console
from .utils import is_cli, load_config
from .config import APPWRITE_CLI_IMAGE, APPWRITE_PLAYWRIGHT_IMAGE
from dataclasses import asdict


@dataclass
class Response:
    message: str
    data: any = None
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

    def get_labs(self):
        """
        Get all labs.
        """
        labs: dict = self.state.get("labs", {})
        return [LabService(**lab) for lab in labs.values()]

    def get_lab(self, name: str) -> LabService | None:
        """
        Get a lab by name.
        """
        labs: dict = self.state.get("labs", {})
        if not (lab := labs.get(name, None)):
            return None
        return LabService(**lab)

    def get_formatted_labs(self, collapsed: bool = False):
        """
        Get all labs.
        """
        labs: dict = self.state.get("labs", {})
        if collapsed:
            headers = ["Name", "Version", "URL", "Admin Email", "Project ID", "API Key"]
            return headers, [
                [
                    val["name"],
                    val["version"],
                    val["url"],
                    val["admin_email"],
                    val["project_id"],
                    val["api_key"],
                ]
                for val in labs.values()
            ]
        return labs

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

    def _deploy_service(
        self,
        project: str,
        template_path: Path,
        env_vars: dict[str, str] = {},
        extra_args: list[str] = [],
    ):
        """
        Barebone deployment of a service.

        Args:
            project: The name of the project to deploy the service to.
            template_path: The path to the template to use for the service.
            env_vars: The environment variables to set.
            extra_args: Extra arguments to pass to the compose command.
        """
        new_env = {**os.environ, **env_vars}
        cmd = [
            self.compose,
            "-f",
            template_path,
            "-p",
            project,
            *extra_args,
            "up",
            "-d",
        ]
        return self._run_cmd_safely(cmd, envs=new_env)

    def _run_cmd_safely(self, cmd: list[str], envs: dict[str, str] = {}):
        """
        Private function to run a command and return the output.

        Args:
            cmd: The command to run.
            envs: The environment variables to set.
        """
        try:
            return run_cmd(cmd, envs)
        except OrchestratorError as e:
            return Response(error=True, message=f"Failed to run command: {e}", data=e)

    def deploy_appwrite_lab(
        self, name: str, version: str, port: int, meta: dict[str, str]
    ):
        """
        Deploy an Appwrite lab.

        Args:
            name: The name to give to the deployment/project.
            version: The version of the service to deploy.
            port: The port to use for the Appwrite service. Must not be in use by another service.
            meta: Extra metadata to pass to the deployment.
        """
        # sync
        appwrite_config = meta.get("appwrite_config", {})

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

        # What actually deploys the service
        cmd_res = self._deploy_service(
            project=name, template_path=template_path, env_vars=env_vars
        )
        # if CLI, will throw error in actual Response object
        if type(cmd_res) is Response and cmd_res.error:
            return cmd_res

        # Get appwrite pods
        project_pods = self.get_running_pods_by_project(name)
        if "appwrite" in project_pods:
            appwrite_pod = project_pods["appwrite"]
            port = appwrite_pod["Ports"].split("/")[0]
            url = f"http://localhost:{port}"
        else:
            url = ""
        lab = LabService(
            name=name,
            version=version,
            url=url,
            **appwrite_config,
        )

        lab.generate_missing_config()
        # Deploy playwright automations for creating user and API key
        api_key_res = self.deploy_playwright_automation(
            lab, Automation.CREATE_USER_AND_API_KEY
        )
        if type(api_key_res) is Response and api_key_res.error:
            api_key_res.message = (
                f"Lab '{name}' deployed, but failed to create API key."
            )
            return api_key_res
        lab.api_key = api_key_res.data

        stored_labs: dict = self.state.get("labs", {}).copy()
        stored_labs[name] = asdict(lab)
        self.state.set("labs", stored_labs)

        return Response(
            error=False,
            message=f"Lab '{name}' deployed.",
            data=lab,
        )

    def deploy_playwright_automation(
        self,
        lab: LabService,
        automation: Automation,
        model: BaseVarModel = None,
        args: list[str] = [],
    ) -> str | Response:
        """
        Deploy playwright automations on a lab (very few automations supported).
        The main one is for creating a user and getting initial API key
        to use for subsequent automation.

        Open to expandability if needed - which is why this function is structured
        this way.

        Args:
            lab: The lab to deploy the automations for.
            automation: The automation to deploy.
            model: The model to use for the automation.
        """
        automation = automation.value
        function = (
            Path(__file__).parent / "automations" / "functions" / f"{automation}.py"
        )
        if not function.exists():
            return Response(
                error=True,
                message=f"Function {automation} not found. This should not happen.",
                data=None,
            )
        automation_dir = Path(__file__).parent / "automations"
        container_work_dir = "/work/automations"
        env_vars = {
            "APPWRITE_URL": lab.url,
            "APPWRITE_PROJECT_ID": lab.project_id,
            "APPWRITE_ADMIN_EMAIL": lab.admin_email,
            "APPWRITE_ADMIN_PASSWORD": lab.admin_password,
            "HOME": container_work_dir,
            **(model.as_dict_with_prefix("APPWRITE") if model else {}),
        }
        envs = " ".join([f"{key}={value}" for key, value in env_vars.items()])
        docker_env_args = []
        for key, value in env_vars.items():
            docker_env_args.extend(["-e", f"{key}={value}"])
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copytree(automation_dir, temp_dir, dirs_exist_ok=True)
            function = Path(temp_dir) / "automations" / "functions" / f"{automation}.py"

            cmd = [
                self.util,
                "run",
                "--network",
                "host",
                # "--rm",
                "-u",
                f"{os.getuid()}:{os.getgid()}",
                "-v",
                f"{temp_dir}:{container_work_dir}",
                *args,
                *docker_env_args,
                APPWRITE_PLAYWRIGHT_IMAGE,
                "python",
                "-m",
                f"automations.functions.{automation}",
            ]
            cmd_res = self._run_cmd_safely(cmd)
            if type(cmd_res) is Response and cmd_res.error:
                cmd_res.message = (
                    f"Failed to deploy playwright automation {automation}."
                )
                return cmd_res
            # If successful, any data should be mounted as result.txt
            result_file = Path(temp_dir) / "result.txt"
            if result_file.exists():
                with open(result_file, "r") as f:
                    data = f.read()
                    return Response(
                        error=False,
                        message=f"Playwright automation{automation} deployed successfully.",
                        data=data,
                    )

    def teardown_service(self, name: str):
        """
        Wind down a service.

        Args:
            name: The name of the service to teardown.
        """
        pods_by_project = self.get_pods_by_project(name)
        if not pods_by_project:
            return Response(
                error=True,
                message=f"Nothing to stop by name of '{name}'.",
                data=None,
            )
        cmd = [self.compose, "-p", name, "down", "-v"]
        cmd_res = self._run_cmd_safely(cmd)
        if type(cmd_res) is Response and cmd_res.error:
            cmd_res.message = f"Failed to teardown lab {name}. \
                        'Please run 'docker-compose -p {name} down -v' manually."
            return cmd_res
        labs: dict = self.state.get("labs", {}).copy()
        labs.pop(name, None)
        self.state.set("labs", labs)

        return Response(
            message=f"Lab '{name}' stopped.",
            data=None,
        )

    def check_pod_status(self, pod_name: str):
        """
        Check the status of a pod.
        """
        pods = self.get_running_pods()
        if pod_name not in pods:
            return False
        return True

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
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, **envs} if envs else None,
        )
        if result.returncode != 0:
            raise OrchestratorError(
                f"An error occured running a command: {result.stderr}"
            )
        return result
    except Exception as e:
        raise OrchestratorError(f"An error occured running a command: {e}")


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
