from dataclasses import dataclass, field
from enum import StrEnum
import random
import string


class Automation(StrEnum):
    CREATE_USER_AND_API_KEY = "create_user_and_api_key"
    CREATE_API_KEY = "create_api_key"
    SYNC_PROJECT = "sync_project"
    # CREATE_USER = "create_user"
    CREATE_PROJECT = "create_project"
    # CREATE_DATABASE = "create_database"
    # CREATE_COLLECTION = "create_collection"
    # CREATE_DOCUMENT = "create_document"
    # CREATE_FUNCTION = "create_function"
    # CREATE_ROLE = "create_role"


class SyncType(StrEnum):
    ALL = "all"
    CONFIG = "settings"
    COLLECTIONS = "collections"
    BUCKETS = "buckets"
    FUNCTIONS = "functions"
    TEAMS = "teams"
    TOPICS = "topics"


@dataclass
class Project:
    project_id: str
    project_name: str
    api_key: str


@dataclass
class LabService:
    name: str
    version: str
    url: str
    admin_email: str = field(default="")
    admin_password: str = field(default="")
    projects: dict[str, Project] = field(
        default_factory=lambda: {"default": Project(None, None, None)}
    )
    _file: str = field(default="")

    def generate_missing_config(self):
        """Generate missing data config with random values."""
        default_project = self.projects["default"]
        
        if not default_project.project_id:
            default_project.project_id = self._generate_random_id()
        
        if not self.admin_email:
            self.admin_email = f"admin_{default_project.project_id}@local.dev"
        
        if not self.admin_password:
            self.admin_password = self._generate_random_password()
        
        if not default_project.project_name:
            default_project.project_name = f"Default_{default_project.project_id}"
    
    def _generate_random_id(self) -> str:
        """Generate a random 10-character ID."""
        return "".join(random.choices(string.ascii_letters + string.digits, k=10)).lower()
    
    def _generate_random_password(self) -> str:
        """Generate a random 16-character password."""
        return "".join(random.choices(string.ascii_letters + string.digits, k=16))
