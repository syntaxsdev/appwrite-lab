import subprocess
import os
from pathlib import Path


class PlaywrightAutomationError(Exception): ...


def run_cmd(
    cmd: list[str], envs: dict[str, str] | None = None
) -> subprocess.CompletedProcess:
    """Run a command and return the output.

    Args:
        cmd: The command to run.
        envs: The environment variables to set.
    """
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env={**os.environ, **envs} if envs else None,
    )

    return result


def env_dict_to_str(envs: dict[str, str]) -> str:
    """
    Convert a dictionary of environment variables to a string.

    Args:
        envs: The dictionary of environment variables.
    """
    return " ".join([f"{key}={value}" for key, value in envs.items()])


def resultify(dir: Path | str, data: str) -> str:
    """
    Convert a string to a result.txt file.

    Args:
        data: The string to convert.
    """
    with open(f"{dir}/result.txt", "w") as f:
        f.write(data)
