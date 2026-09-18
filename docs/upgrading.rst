=============================
Upgrade an existing Rola host
=============================

This upgrade consolidates the host, domain apps and frontend into one repository.
It also moves contest confirmation configuration into the host integration app.
Existing user primary keys, public UUIDs, app labels and domain data are retained.

Prepare the database and files
==============================

Back up the database and uploaded media, and verify that the backup can be
restored. Rehearse the upgrade on an isolated restored copy. Stop web processes
and background workers while applying the schema transition so submissions
cannot change during the copy and validation steps.

If upgrading PostgreSQL, use a supported dump/restore or ``pg_upgrade`` workflow.
Do not point the new Compose database image at an older major version's data
directory. The consolidated Compose project uses new volumes; it does not
import a database or media from another Compose project automatically.

Build the backend image or install ``backend/pyproject.toml`` and configure the
host to connect to the restored database. Retain the existing ``drf_user`` app
and ``AUTH_USER_MODEL = "drf_user.User"`` for this migration.

Adopt the portable migrations
=============================

Run from ``backend`` before ordinary ``migrate``:

.. code-block:: console

   python manage.py upgrade_legacy_rolca
   python manage.py migrate --noinput
   python manage.py createcachetable
   python manage.py collectstatic --noinput

The upgrade command uses the preserved historical migration modules to advance
a recognized legacy database. It creates the host-owned ``ContestNotification``
records, copies existing template associations, and verifies those associations
before removing the old contest column. It then checks the resulting schema
before recording the portable migration baselines.

The command supports rerunning after an interrupted upgrade. It rejects unknown
migration histories or incompatible schemas instead of guessing that an existing
table matches a new initial migration. If validation fails, investigate on the
restored copy; do not work around the checks with ``--fake``.

Ordinary ``migrate`` rejects legacy databases that have not completed adoption.
For a genuinely empty database, run ordinary ``migrate`` directly.

Update deployment and clients
=============================

The host keeps ``/api/v1`` and the existing token authentication protocol. Read
the account API changes below and regenerate frontend types when changing the
backend schema. Deploy the backend and the updated frontend as a coordinated
release.

Replace obsolete Django storage, email and CORS settings with the environment
configuration in :doc:`deployment`. Python dependencies now come from
``backend/pyproject.toml``. The frontend uses npm and Vite; rebuild its static
assets with the intended public API and payment configuration.

The backend now runs under Gunicorn, uses database sessions and shares throttle
state through Django's database cache. The ``createcachetable`` command above
creates the required ``rola_cache`` table.

Stop any old backup worker before deploying this version. The application no
longer includes backup processing or requires Redis. Remove the old Redis
service configuration if no other application uses it. The upgrade does not
delete historical backup records or stored backup files. A migration removes
the retired backup table's foreign-key constraint on uploaded files so those
records cannot block normal file deletion. Continue backing up the database
and uploaded media through your deployment's backup procedures.

Check the following against the restored deployment before switching traffic:

* Registration, activation, login, account updates and password reset.
* Existing contest confirmation templates in Django admin.
* Image upload, submission grouping and payment status.
* Judge assignments, scoring, publication and contest exports.
* Static files, original images and thumbnails.
* Email delivery with your actual provider.

Account API changes
===================

The endpoint paths and token protocol remain, with these intentional changes:

* Profile location fields are present and nullable when an account has no location.
* Profile updates reject a password field with HTTP 400. Use ``change_password``.
* Password-reset requests return the same empty HTTP 200 response for active,
  unknown and inactive addresses. Invalid signed payloads return HTTP 400.
* Password changes and resets expire existing login tokens and invalidate old
  password-reset links. Reset consumption is checked atomically.
* Login, account creation and recovery are rate limited by caller address. Exceeding a
  configured rate returns HTTP 429.
* Activation and reset emails point to frontend pages under
  ``ROLA_FRONTEND_URL``. The old unimplemented backend placeholders are removed.

The checked-in OpenAPI schema describes the current requests and responses.

Rollback
========

Repository consolidation does not provide an automatic downgrade of production
data. Keep the previous application images and a verified pre-upgrade database
and media backup. If the rehearsal reveals a failure, stop and fix it before
switching production traffic. A rollback after the migration requires restoring
compatible application and database state together.
