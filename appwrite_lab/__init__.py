from .labs import Labs

_labs: Labs | None = None
is_cli: bool = False


def get_global_labs() -> Labs:
    global _labs
    if not _labs:
        _labs = Labs()
    return _labs


def set_cli_true():
    global is_cli
    is_cli = True


__all__ = ["Labs", "get_labs"]
