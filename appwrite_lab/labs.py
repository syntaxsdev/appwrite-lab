from ._state import State
from ._orchestrator import ServiceOrchestrator
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
            return False
        if appwrite_json == "appwrite.json":
            appwrite_json = Path.cwd() / appwrite_json

        if not os.path.exists(appwrite_json):
            return False

        return self.orchestrator.sync_appwrite_config(lab, appwrite_json, sync_type)

    def stop(self, name: str):
        return self.orchestrator.teardown_service(name)
