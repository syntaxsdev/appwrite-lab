import os
import re
import shutil
import subprocess
import json
import tempfile
from pathlib import Path

from appwrite_lab.automations.models import BaseVarModel, AppwriteAPIKeyCreation
from ._state import State
from dataclasses import dataclass
from .models import Lab, Automation, SyncType, Project
from dotenv import dotenv_values
from appwrite_lab.utils import console
from .utils import is_cli
from .config import APPWRITE_PLAYWRIGHT_IMAGE
from dataclasses import asdict


@dataclass
class Response:
    message: str
    data: any = None
    error: bool = False
    _print_data: bool = False

    def __post_init__(self):
        if is_cli:
            if self.error:
                console.print(self.message, style="red")
            else:
                console.print(
                    self.message if not self._print_data else self.data, style="green"
                )


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
        return [Lab(**lab) for lab in labs.values()]

    def get_lab(self, name: str) -> Lab | None:
        """
        Get a lab by name.
        """
        labs: dict = self.state.get("labs", {})
        if not (lab := labs.get(name, None)):
            return None
        projects = lab.get("projects", {})
        _projects = {key: Project(**project) for key, project in projects.items()}
        return Lab(**{**lab, "projects": _projects})

    def get_formatted_labs(self, collapsed: bool = False):
        """
        Get all labs.
        """
        labs: dict = self.state.get("labs", {})
        if collapsed:
            headers = [
                "Lab Name",
                "Version",
                "URL",
                "Admin Email",
                "Admin Password",
                "Project ID",
            ]
            data = []
            for val in labs.values():
                project = Project(**val.get("projects", {}).get("default"))
                data.append(
                    [
                        val["name"],
                        val["version"],
                        val["url"],
                        val["admin_email"],
                        val["admin_password"],
                        project.project_id,
                    ]
                )
            return headers, data
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

    def deploy_appwrite_lab(
        self,
        name: str,
        version: str,
        port: int,
        meta: dict[str, str],
        **kwargs: dict[str, str],
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

        # What actually deploys the initial appwrite service
        cmd_res = self._deploy_service(
            project=name, template_path=template_path, env_vars=env_vars
        )
        # if CLI, will throw error in actual Response object
        if type(cmd_res) is Response and cmd_res.error:
            return cmd_res

        # Get appwrite pods
        project_pods = self.get_running_pods_by_project(name)
        if traefik_pod := project_pods.get("appwrite-traefik", None):
            ports = traefik_pod["Ports"].split(",")
            port = extract_port_from_pod_info(traefik_pod)
            assert len(ports) > 1, OrchestratorError(
                "Failed to extract port from pod info."
            )
            port = extract_port_from_pod_info(traefik_pod)
            url = f"http://localhost:{port}"
        else:
            url = ""
        proj_id = appwrite_config.pop("project_id", None)
        proj_name = appwrite_config.pop("project_name", None)
        _kwargs = {
            **appwrite_config,
            "projects": {"default": Project(proj_id, proj_name, None)},
        }
        lab = Lab(
            name=name,
            version=version,
            url=url,
            **_kwargs,
        )

        lab.generate_missing_config()
        # ensure project_id and project_name are set
        proj_id = proj_id or lab.projects.get("default").project_id
        proj_name = proj_name or lab.projects.get("default").project_name
        if kwargs.get("just_deploy", False):
            return Response(
                error=False,
                message=f"Lab '{name}' deployed with --just-deploy flag.",
                data=lab,
            )
        # Deploy playwright automations for creating user and API key
        api_key_res = self.deploy_playwright_automation(
            lab=lab,
            automation=Automation.CREATE_USER_AND_API_KEY,
            model=AppwriteAPIKeyCreation(
                key_name="default_key", project_name=proj_name, key_expiry="Never"
            ),
        )
        if type(api_key_res) is Response and api_key_res.error:
            api_key_res.message = f"Lab '{name}' deployed, but failed to create API key. Spinning down lab."
            self.teardown_service(name)
            return api_key_res
        lab.projects["default"].api_key = api_key_res.data

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
        lab: Lab,
        automation: Automation,
        project: Project | None = None,
        model: BaseVarModel = None,
        args: list[str] = [],
        *,
        print_data: bool = False,
        **kwargs,
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
            model: The model args to use for the automation.
            args: Extra arguments to the container.
            project: The project to use for the automation, if not provided, the default project is used.

        Keyword Args:
            print_data: Whether to print the data of the response instead of the message.
        """
        automation = automation.value
        function = (
            Path(__file__).parent / "automations" / "scripts" / f"{automation}.py"
        )
        if not function.exists():
            return Response(
                error=True,
                message=f"Function {automation} not found. This should not happen.",
                data=None,
            )
        automation_dir = Path(__file__).parent / "automations"
        container_work_dir = "/work/automations"
        project = project or lab.projects["default"]
        project = Project(**project) if isinstance(project, dict) else project
        proj_id = project.project_id
        api_key = project.api_key

        env_vars = {
            "APPWRITE_URL": lab.url,
            "APPWRITE_PROJECT_ID": proj_id,
            "APPWRITE_ADMIN_EMAIL": lab.admin_email,
            "APPWRITE_ADMIN_PASSWORD": lab.admin_password,
            "APPWRITE_API_KEY": api_key,
            "APPWRITE_PROJECT_NAME": project.project_name,
            "HOME": container_work_dir,
            **(model.as_dict_with_prefix("APPWRITE") if model else {}),
        }
        docker_env_args = []
        for key, value in env_vars.items():
            docker_env_args.extend(["-e", f"{key}={value}"])
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copytree(automation_dir, temp_dir, dirs_exist_ok=True)
            function = Path(temp_dir) / "automations" / "scripts" / f"{automation}.py"
            cmd = [
                self.util,
                "run",
                "--network",
                "host",
                "--rm",
                "-u",
                f"{os.getuid()}:{os.getgid()}",
                "-v",
                f"{temp_dir}:{container_work_dir}:Z",
                *args,
                *docker_env_args,
                APPWRITE_PLAYWRIGHT_IMAGE,
                "python",
                "-m",
                f"automations.scripts.{automation}",
            ]
            cmd_res = self._run_cmd_safely(cmd)
            if type(cmd_res) is Response and cmd_res.error:
                cmd_res.message = (
                    f"Failed to deploy playwright automation {automation}."
                )
                return cmd_res
            # If successful, any data should be mounted as result.txt
            result_file = Path(temp_dir) / "result.txt"
            _data = None
            if result_file.exists():
                with open(result_file, "r") as f:
                    _data = f.read()
            return Response(
                error=False,
                message=f"Playwright automation {automation} deployed successfully.",
                data=_data,
                _print_data=print_data,
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
        cmd = [
            self.compose,
            "-p",
            name,
            "down",
            "-v",
            "--timeout",
            "0",
            "--remove-orphans",
        ]
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
            return Response(error=True, message=f"{str(e)}", data=str(e))

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
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, **envs} if envs else None,
    )
    if result.returncode != 0:
        error_msg = result.stderr.strip()
        if error_msg:
            # Look for the actual error message in the traceback
            lines = error_msg.split("\n")
            for line in reversed(lines):
                if "PlaywrightAutomationError:" in line or "OrchestratorError:" in line:
                    # Extract just the error message part
                    if ":" in line:
                        error_msg = line.split(":", 1)[1].strip()
                    break
        raise OrchestratorError(f"An error occured running a command: {error_msg}")
    return result


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


def extract_port_from_pod_info(pod_info: dict) -> int:
    """Extract port from pod information returned by get_running_pods_by_project.

    Args:
        pod_info: The pod information to extract the port from.
    """
    if "Ports" in pod_info:
        # Handle format like "0.0.0.0:8005->80/tcp"
        ports_str = pod_info["Ports"]
        match = re.search(r":(\d+)->80/tcp", ports_str)
        if match:
            return int(match.group(1))
    raise OrchestratorError(f"Failed to extract port from pod info: {pod_info}")
