from dataclasses import dataclass


@dataclass
class LabService:
    name: str
    version: str
    url: str
    admin_email: str = ""
    admin_password: str = ""
    project_id: str = ""
    project_name: str = ""
    _file: str = ""
