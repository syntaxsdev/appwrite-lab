from .utils import run_cmd, env_dict_to_str
from dataclasses import dataclass


@dataclass
class CommandExecutor:
    cmd: list[str]
    envs: dict[str, str] | None = None

    def run(self):
        return run_cmd(self.cmd, self.envs)

    def __call__(self):
        return self.run()


class AppwriteCLI:
    def login(self, url: str, email: str, password: str) -> CommandExecutor:
        """
        Login to Appwrite.

        Args:
            url: The URL of the Appwrite instance.
            email: The email of the user.
            password: The password of the user.

        Returns:
            bool: True if login was successful, False otherwise.
        """
        cmd = [
            "appwrite",
            "login",
            "--endpoint",
            url,
            "--email",
            email,
            "--password",
            password,
        ]
        return CommandExecutor(cmd)

    def get_project(self, project_id: str) -> CommandExecutor:
        """
        Get a project from Appwrite.

        Args:
            project_id: The ID of the project.
        """
        cmd = ["appwrite", "projects", "get", "--project-id", project_id]
        return CommandExecutor(cmd)


def execute_same_shell(*execs: CommandExecutor) -> list[str]:
    """
    Run a batch of commands in the same shell and return the outputs.

    Args:
        execs: The commands to run.
    """
    all_cmds = []
    for exc in execs:
        cmds = exc.cmd.copy()
        if exc.envs:
            # Prepend environment variables to the command
            env_str = env_dict_to_str(exc.envs)
            cmds.insert(0, env_str)
        all_cmds.append(" ".join(cmds))
    
    # Join all commands with && to run in same shell
    combined_cmd = " && ".join(all_cmds)
    return run_cmd(["bash", "-c", combined_cmd])
