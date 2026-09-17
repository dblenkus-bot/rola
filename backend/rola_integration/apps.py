"""Rola integration application configuration."""

from django.apps import AppConfig
from django.db.models.signals import pre_migrate


class RolaIntegrationConfig(AppConfig):
    """Register host behavior and protect legacy database upgrades."""

    name = "rola_integration"
    default_auto_field = "django.db.models.AutoField"

    def ready(self) -> None:
        """Check migration history only when migration is explicitly invoked."""
        from .migration_guard import require_legacy_upgrade

        pre_migrate.connect(require_legacy_upgrade, sender=self)
