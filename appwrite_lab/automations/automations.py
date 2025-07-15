from appwrite_lab.models import Lab
from appwrite.client import Client


class LabContext:
    def __init__(self, lab: Lab):
        self.lab = lab
        self.client = (
            Client()
            .set_endpoint(lab.url)
            .set_project(lab.project_id)
            .set_key(lab.api_key)
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class AppwriteAutomation:
    def __init__(self):
        pass

    def create_user(self):
        pass
