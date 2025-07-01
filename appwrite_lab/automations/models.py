from dataclasses import dataclass
import uuid


@dataclass
class AppwriteUserCreation:
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