import json
import os
from pathlib import Path

from .utils import get_state_path


class StateError(Exception): ...


class State:
    def __init__(self, path: str | None = None):
        """
        Initialize the state manager

        Args:
            path: The path to the state file.
        """
        if not path:
            path = get_state_path()

        self.path: str = path
        self.data: dict[str, any] = {}
        if not os.path.exists(self.path):
            try:
                with open(self.path, "w") as f:
                    f.write("{}")
            except Exception as e:
                raise StateError(f"Failed to create state file: {e}")
        else:
            try:
                with open(self.path, "r") as f:
                    self.data = json.load(f)
            except Exception as e:
                raise StateError(f"Failed to load state file: {e}")

    def save(self):
        """
        Save the state to the file.
        """
        with open(self.path, "w") as f:
            json.dump(self.data, f)

    def get(self, key: str, default: any = None):
        """
        Get a value from the state.

        Args:
            key: The key to get the value for.

        Returns:
            The value for the key.
        """
        return self.data.get(key, default)

    def set(self, key: str, value: any):
        """
        Set a value in the state.
        """
        self.data[key] = value
        self.save()
