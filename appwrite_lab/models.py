from dataclasses import dataclass, field
from enum import StrEnum
import random
import string


class Automation(StrEnum):
    CREATE_USER_AND_API_KEY = "create_user_and_api_key"
    CREATE_API_KEY = "create_api_key"
    SYNC_PROJECT = "sync_project"
    CREATE_USER = "create_user"
    CREATE_PROJECT = "create_project"
    CREATE_DATABASE = "create_database"
    CREATE_COLLECTION = "create_collection"
    CREATE_DOCUMENT = "create_document"
    CREATE_FUNCTION = "create_function"
    # CREATE_TRIGGER = "create_trigger"
    CREATE_ROLE = "create_role"


class SyncType(StrEnum):
    ALL = "all"
    CONFIG = "settings"
    COLLECTIONS = "collections"
    BUCKETS = "buckets"
    FUNCTIONS = "functions"
    TEAMS = "teams"
    TOPICS = "topics"


@dataclass
class LabService:
    name: str
    version: str
    url: str
    admin_email: str = field(default="")
    admin_password: str = field(default="")
    project_id: str = field(default="")
    project_name: str = field(default="")
    api_key: str = field(default="")
    _file: str = field(default="")

    def generate_missing_config(self):
        """
        Generate missing data config with random.
        """
        if not self.project_id:
            self.project_id = "".join(
                random.choices(string.ascii_letters + string.digits, k=10)
            )
            self.project_id = self.project_id.lower()
        if not self.admin_email:
            self.admin_email = f"admin_{self.project_id}@local.dev"
        if not self.admin_password:
            self.admin_password = "".join(
                random.choices(string.ascii_letters + string.digits, k=16)
            )
        if not self.project_name:
            self.project_name = f"Default_{self.project_id}"
