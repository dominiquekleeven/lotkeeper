from pathlib import Path


def find_project_root(start_path: Path = Path(__file__)) -> Path:
    """Find the project root by looking for marker files

    Args:
        start_path: The path to start the search from

    Returns:
        The project root
    """
    current = start_path.parent
    while current != current.parent:
        if any((current / marker).exists() for marker in ["pyproject.toml", ".env"]):
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")
