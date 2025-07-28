from appwrite_lab.utils import load_config
from ._state import State
from ._orchestrator import ServiceOrchestrator, Response
from .models import Automation, Lab
from appwrite_lab.automations.models import (
    AppwriteLabCreation,
    AppwriteProjectCreation,
    AppwriteSyncProject,
    AppwriteAPIKeyCreation,
    Expiration,
)
from .models import Project

from pathlib import Path

import os


class Labs:
    def __init__(self):
        self.state = State()
        self.orchestrator = ServiceOrchestrator(self.state)

    def new(
        self,
        name: str,
        version: str,
        port: int,
        auth: AppwriteLabCreation | None = None,
        just_deploy: bool = False,
    ):
        """
        Deploy a new Appwrite lab.

        Args:
            name: The name of the lab.
            version: The version of the lab.
            port: The port of the lab.
            auth: The authentication credentials.
            just_deploy: Deploy the lab without creating an API key or project.
        """
        return self.orchestrator.deploy_appwrite_lab(
            name, version, port, auth, just_deploy=just_deploy
        )

    def get_lab(self, name: str) -> Lab | None:
        """
        Get a lab by name.

        Args:
            name: The name of the lab.
        """
        return self.orchestrator.get_lab(name)

    def sync_with_appwrite_config(
        self,
        name: str,
        appwrite_json: str,
        sync_type: str = "all",
        expiration: Expiration = Expiration.THIRTY_DAYS,
    ):
        lab = self.orchestrator.get_lab(name)
        if not lab:
            return Response(
                error=True,
                message=f"Lab {name} not found",
            )
        if appwrite_json == "appwrite.json":
            appwrite_json = Path.cwd() / appwrite_json

        if not os.path.exists(appwrite_json):
            return Response(
                error=True,
                message="Appwrite config file not found in current directory.",
            )

        try:
            ajson: dict = load_config(appwrite_json)
            proj_name = ajson.get("projectName")
            proj_id = ajson.get("projectId")
            if not proj_name:
                return Response(
                    error=True,
                    message="Appwrite config file does not define a project name.",
                )
        except Exception as e:
            return Response(
                error=True,
                message=f"Failed to load appwrite config: {e}",
            )

        apc = AppwriteProjectCreation(
            project_name=proj_name,
            project_id=proj_id,
        )
        addn_args = ["-v", f"{appwrite_json}:/work/appwrite.json"]
        self.orchestrator.deploy_playwright_automation(
            lab=lab, automation=Automation.CREATE_PROJECT, model=apc, args=addn_args
        )
        self.orchestrator.deploy_playwright_automation(
            lab=lab,
            automation=Automation.SYNC_PROJECT,
            model=AppwriteSyncProject(sync_type),
            args=addn_args,
        )
        key_name = f"{proj_name}-key"
        key = self.create_api_key(
            lab=lab, expiration=expiration, project_name=proj_name, key_name=key_name
        )
        lab.projects[proj_name] = Project(
            project_id=proj_id,
            project_name=proj_name,
            api_key=key.data,
        )
        labs = self.state.get("labs")
        labs[name] = lab.to_dict()
        self.state.set("labs", labs)

    def create_api_key(
        self,
        project_name: str,
        key_name: str,
        expiration: Expiration = "30 days",
        lab_name: str | None = None,
        lab: Lab | None = None,
    ) -> Response:
        """
        Create an API key for a project.

        Args:
            lab_name: The name of the lab.
            project_name: The name of the project.
            expiration: The expiration of the API key.
        """
        lab = lab or self.orchestrator.get_lab(lab_name)
        if not lab:
            return Response(message=f"Lab {lab_name} not found", error=True)
        api_key = self.orchestrator.deploy_playwright_automation(
            lab=lab,
            automation=Automation.CREATE_API_KEY,
            model=AppwriteAPIKeyCreation(
                project_name=project_name,
                key_name=key_name,
                key_expiry=str(expiration.value),
            ),
            print_data=True,
        )
        if api_key.error:
            return Response(
                message=f"Failed to create API key: {api_key.message}", error=True
            )
        return Response(
            message=f"API key created for {project_name}",
            data=api_key.data,
            _print_data=True,
        )

    def stop(self, name: str):
        return self.orchestrator.teardown_service(name)

    def create_project(
        self,
        project_name: str,
        project_id: str,
        *,
        lab_name: str | None = None,
        lab: Lab | None = None,
    ):
        """
        Create a project.

        Args:
            project_name: The name of the project.
            project_id: The ID of the project.

        Keyword Args:
            lab_name: The name of the lab.
            lab: The lab object.
        """
        lab = lab or self.orchestrator.get_lab(lab_name)
        if not lab:
            return Response(message=f"Lab {lab_name} not found", error=True)
        apc = AppwriteProjectCreation(
            project_name=project_name,
            project_id=project_id,
        )
        return self.orchestrator.deploy_playwright_automation(
            lab=lab,
            automation=Automation.CREATE_PROJECT,
            project=Project(project_id=project_id, project_name=project_name),
            model=apc,
        )
