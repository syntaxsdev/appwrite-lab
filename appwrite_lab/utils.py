import os


def ensure_dir():
    """Ensure APPWRITE directory exists."""
    os.makedirs(os.path.expanduser("~/.appwrite-lab"), exist_ok=True)
    return True
