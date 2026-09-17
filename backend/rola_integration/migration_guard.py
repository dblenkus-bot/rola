"""Prevent a portable initial migration from recreating legacy tables."""

from django.apps import apps
from django.conf import settings
from django.core.management.base import CommandError
from django.db import connections
from django.db.migrations.recorder import MigrationRecorder

from .migration_settings import LEGACY_MIGRATION_MODULES, PORTABLE_MIGRATIONS


def require_legacy_upgrade(sender, using: str, **kwargs) -> None:
    """Reject ordinary migration on a database requiring explicit adoption.

    Parameters
    ----------
    sender : AppConfig
        Integration app sending the pre-migration signal.
    using : str
        Database alias being migrated.
    **kwargs : object
        Additional Django signal arguments.

    Raises
    ------
    CommandError
        If legacy records exist without a complete portable baseline.
    """
    if settings.MIGRATION_MODULES.get("core") == LEGACY_MIGRATION_MODULES["core"]:
        return
    applied = set(MigrationRecorder(connections[using]).applied_migrations())
    legacy = {
        key for key in applied if key[0] in LEGACY_MIGRATION_MODULES
    } - PORTABLE_MIGRATIONS
    installed = {app.label for app in apps.get_app_configs()}
    required = {key for key in PORTABLE_MIGRATIONS if key[0] in installed}
    if legacy and not required <= applied:
        raise CommandError(
            "This database uses Rolca's legacy migrations. Run "
            "'python manage.py upgrade_legacy_rolca' before 'migrate'."
        )
