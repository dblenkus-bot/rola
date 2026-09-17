"""Register operational checks for the host."""

from django.apps import AppConfig


class UtilsConfig(AppConfig):
    """Load deployment checks without changing database behavior."""

    name = "utils"

    def ready(self):
        """Register the host deployment checks."""
        from . import checks  # noqa: F401
