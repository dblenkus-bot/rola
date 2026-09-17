============
Rola backend
============

Django host and domain apps for the Rola photography contest platform.

Install this directory with ``python -m pip install .``. Runtime and development
dependency groups are declared in ``pyproject.toml``. Configure the deployment
environment and use ``rola.settings`` as ``DJANGO_SETTINGS_MODULE``.

See the repository's ``docs`` directory for development, deployment, integration
and database-upgrade instructions. Existing Rolca databases require the explicit
``upgrade_legacy_rolca`` transition before ordinary migration.
