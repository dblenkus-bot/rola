Unreleased
==========

* Upgrade to Python 3.12–3.14, Django 6.1, DRF 3.18, django-filter 26,
  Pillow 12 and psycopg 3.
* Move packaging to pyproject.toml and replace pkg_resources metadata access.
* Make domain apps independent of the host's account and email models, with
  explicit adoption of historical migrations for existing Rola databases.
* Fix author listing, submission validation and permissions, transactional batch
  creation, filtering, export, rating validation, and PostgreSQL judging order.
* Modernize thumbnail generation, including historical migration 0017.
* Add workflow, media, migration, payment and judging tests.
* Modernize CI, documentation, linters and local PostgreSQL services.
* Remove the backup app, Channels worker and Redis dependency. Serve Django
  through Gunicorn with database sessions and a shared database throttle cache.

See upgrading.rst for host configuration and deployment requirements.
