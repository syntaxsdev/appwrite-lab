from ._state import State
from ._orchestrator import ServiceOrchestrator


class Labs:
    def __init__(self):
        self.state = State()
        self.orchestrator = ServiceOrchestrator(self.state)

    def new(self, name: str, version: str, port: int):
        return self.orchestrator.deploy_service(name, version, port)

    def get_lab(self, name: str):
        return self.orchestrator.get_running_pods().get(name)

    def stop(self, name: str):
        return self.orchestrator.wind_down_service(name)