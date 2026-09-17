====================
Develop and validate
====================

Use a Python version supported by ``backend/pyproject.toml`` and the Node.js
version in ``frontend/.node-version``. Docker Compose supplies PostgreSQL and
Redis for database and worker integration tests.

Run the development stack
=========================

Copy ``.env.example`` to ``.env`` and replace its placeholder values. Do not
commit your local environment file. Run from the repository root:

.. code-block:: console

   docker compose up --build
   docker compose run --rm backend python manage.py createsuperuser

Open http://localhost:8080. The frontend development server proxies API, admin
and media requests to Django. Source directories are mounted for live reload.

PostgreSQL and Redis are published only on loopback. Their local ports can be
changed in ``.env`` if another development stack already uses them. Stopping
containers retains the database and uploaded media volumes.

After ``package-lock.json`` changes, refresh dependencies in the frontend's
named volume and restart the development server:

.. code-block:: console

   docker compose stop frontend
   docker compose run --rm --no-deps frontend npm ci
   docker compose up -d frontend

This refreshes the dependency volume without deleting database or media volumes.

Native development
==================

Create a virtual environment and install the declared backend dependencies:

.. code-block:: console

   python -m venv .venv
   .venv/bin/python -m pip install -e './backend[test,lint,docs,package]'
   docker compose up -d db redis

Set ``ROLA_SECRET_KEY``, ``ROLA_DEBUG=true``, ``ALLOWED_HOSTS`` and the
``ROLA_POSTGRESQL_*`` connection variables in your shell. Native commands do not
automatically load ``.env``. Set ``ROLA_REDIS_HOST=127.0.0.1`` and the published
Redis port when running Django outside Compose.
Set ``ROLA_FRONTEND_URL=http://localhost:5173`` so account emails link to the
frontend development server. Adjust it if you change that server's address.

.. code-block:: console

   cd backend
   ../.venv/bin/python manage.py migrate
   ../.venv/bin/python manage.py runserver

In another terminal, start the frontend from its directory:

.. code-block:: console

   npm ci
   npm run dev

The default development proxy targets Django on localhost. Set
``API_PROXY_TARGET`` to use another backend address.

Backend checks
==============

Run these commands from ``backend`` with the virtual environment activated:

.. code-block:: console

   python -m pip check
   python -m ruff check .
   python -m ruff format --check .
   python -m mypy
   python -m pytest -W error::DeprecationWarning
   python manage.py check --settings=rola.test_settings
   python manage.py makemigrations --check --dry-run --settings=rola.test_settings

The test settings use SQLite for lightweight checks. To validate database
behavior against PostgreSQL, set ``ROLA_TEST_POSTGRESQL=true`` and the
``ROLA_POSTGRESQL_*`` variables before running pytest. The database user must
be able to create and drop a test database. Use an isolated development server.
Set ``ROLCA_REDIS_URL`` to run the real Redis transport test.

Frontend checks
===============

Run from ``frontend``:

.. code-block:: console

   npm ci
   npm run lint
   npm run format:check
   npm run typecheck
   npm test -- --run
   npm run build

TypeScript stays on the newest release supported by the API generator and
linting toolchain. The package manifest records that compatibility choice.

Update the API contract
=======================

After changing serializers, endpoints or their schema annotations, regenerate
the schema and frontend types:

.. code-block:: console

   cd backend
   ../.venv/bin/python manage.py spectacular --settings=rola.test_settings --file openapi.yaml --validate --fail-on-warn
   cd ../frontend
   npm run api:generate

Review both generated diffs with the implementation. API changes must include
updated frontend handling and tests for affected response shapes, nullability,
validation and permissions. CI checks that regeneration leaves no diff.

Documentation and packaging
===========================

Run from the repository root with the virtual environment activated:

.. code-block:: console

   python -m sphinx -W --keep-going -b html docs docs/_build/html
   python -m build backend
   python -m twine check backend/dist/*

CI runs the supported Python matrix, frontend checks, schema drift checks and
both production image builds. Dependency declarations belong in the manifests;
do not add hand-maintained lists of transitive Python dependencies.
