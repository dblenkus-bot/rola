============
Rola backend
============

Django host and domain apps for the Rola photography contest platform.

Install this directory with ``python -m pip install .``. Runtime and development
dependency groups are declared in ``pyproject.toml``. Configure the deployment
environment and use ``rola.settings`` as ``DJANGO_SETTINGS_MODULE``.

Apply migrations and run ``python manage.py createcachetable`` before starting
the server. Production uses Gunicorn with ``rola.wsgi:application``. Sessions
and the shared throttle cache use the configured database.

See the repository's ``docs`` directory for development, deployment, integration
and manual data-transfer instructions. Migrations initialize a new database;
existing Rolca data must be transferred separately.
