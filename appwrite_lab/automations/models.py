from dataclasses import dataclass, asdict
import uuid
import os
from enum import Enum


class Expiration(str, Enum):
    NEVER = "Never"
    SEVEN_DAYS = "7 Days"
    THIRTY_DAYS = "30 days"
    NINETY_DAYS = "90 days"
    YEAR = "Year"


@dataclass
class BaseVarModel:
    def as_dict(self):
        """Convert the model to a dictionary."""
        temp = asdict(self)
        # uppercase all keys
        return {k.upper(): v for k, v in temp.items()}

    def as_dict_with_prefix(self, prefix: str = "APPWRITE"):
        """Convert the model to a dictionary with a prefix."""
        temp = asdict(self)
        # uppercase all keys
        return {f"{prefix}_{k.upper()}": v for k, v in temp.items()}

    @classmethod
    def from_env(cls):
        """
        Create a model from the environment variables.
        """
        # Get field names from the dataclass
        field_names = [field.name for field in cls.__dataclass_fields__.values()]

        # Build kwargs dict by mapping environment variables to field names=
        kwargs = {}
        for field_name in field_names:
            env_key = f"APPWRITE_{field_name.upper()}"

            if env_val := os.environ.get(env_key, None):
                kwargs[field_name] = env_val
        return cls(**kwargs)


@dataclass
class AppwriteWebAuth(BaseVarModel):
    url: str
    admin_email: str
    admin_password: str


@dataclass
class AppwriteProjectCreation(BaseVarModel):
    project_id: str
    project_name: str


@dataclass
class AppwriteSyncProject(BaseVarModel):
    resource: str


@dataclass
class AppwriteAPIKeyCreation(BaseVarModel):
    project_name: str
    key_name: str
    key_expiry: Expiration


@dataclass
class AppwriteUserCreation(BaseVarModel):
    url: str
    admin_email: str
    admin_password: str
    project_id: str
    project_name: str

    def generate(self):
        """Generate random data for model"""
        random_key = str(uuid.uuid4())
        password = random_key[:16]
        last_six = random_key[-6:]
        admin_password = password
        admin_email = f"admin{last_six}@local.dev"
        project_id = random_key
        project_name = f"test-project-{last_six}"

        return AppwriteUserCreation(
            admin_email=admin_email,
            admin_password=admin_password,
            project_id=project_id,
            project_name=project_name,
        )
