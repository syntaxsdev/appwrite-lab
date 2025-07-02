from appwrite_lab.utils import load_config
from ._state import State
from ._orchestrator import ServiceOrchestrator, Response
from .models import Automation
from appwrite_lab.automations.models import AppwriteProjectCreation, AppwriteSyncProject

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
        meta: dict[str, str] = {},
    ):
        """
        Deploy a new Appwrite lab.

        Args:
            name (str): The name of the lab.
            version (str): The version of the lab.
            port (int): The port of the lab.
        """
        return self.orchestrator.deploy_appwrite_lab(name, version, port, meta)

    def sync_with_appwrite_config(
        self, name: str, appwrite_json: str, sync_type: str = "all"
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
            vars = AppwriteProjectCreation(
                project_name=proj_name,
                project_id=proj_id,
            )
        except Exception as e:
            return Response(
                error=True,
                message=f"Failed to load appwrite config: {e}",
            )
        addn_args = ["-v", f"{appwrite_json}:/work/appwrite.json"]
        self.orchestrator.deploy_playwright_automation(
            lab, Automation.CREATE_PROJECT, model=vars, args=addn_args
        )
        self.orchestrator.deploy_playwright_automation(
            lab,
            Automation.SYNC_PROJECT,
            model=AppwriteSyncProject(sync_type),
            args=addn_args,
        )

    def stop(self, name: str):
        return self.orchestrator.teardown_service(name)
