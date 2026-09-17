"""Read typed application environment variables."""

import os


def boolean(name: str, default: bool = False) -> bool:
    """Read a boolean, rejecting empty strings and ambiguous values."""
    value = os.environ.get(name)
    if value is None:
        return default
    if value.lower() in {"true", "1", "yes", "on"}:
        return True
    if value.lower() in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean.")


def comma_separated(name: str, default: str = "") -> list[str]:
    """Read nonempty items from a comma-separated environment value."""
    return [
        item.strip()
        for item in os.environ.get(name, default).split(",")
        if item.strip()
    ]
