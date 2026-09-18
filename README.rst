====
Rola
====

Rola runs photography contests, submissions, judging and published results.
This repository contains the Django host, Rolca's domain apps and the React
frontend. Backend and frontend builds remain separate.

Start development
=================

Install Docker with Compose, then run:

.. code-block:: console

   cp .env.example .env

Replace the two placeholder values in ``.env`` with local development secrets.
Start the complete development stack:

.. code-block:: console

   docker compose up --build
   docker compose run --rm backend python manage.py createsuperuser

Open http://localhost:8080. Django admin is at
http://localhost:8080/django-admin/.

See ``docs/contributing.rst`` for native development and verification commands.
Read ``docs/upgrading.rst`` before connecting an existing database. PostgreSQL
major-version upgrades require a database migration; existing data directories
must not be mounted into a different PostgreSQL major version.

Layout
======

* ``backend/rola`` contains settings and host routing.
* ``backend/drf_user`` contains the current account and authentication app.
* ``backend/rolca`` contains the reusable contest, rating and payment apps.
* ``backend/rola_integration`` connects Rolca to this host's account and email models.
* ``frontend`` contains the React application and generated API types.
* ``docs`` contains development, integration, deployment and upgrade instructions.

Python dependency declarations are in ``backend/pyproject.toml``. JavaScript
packages are declared in ``frontend/package.json`` and resolved by its npm
lockfile. The imported repositories' Git histories remain available through
the consolidation merge commits.
