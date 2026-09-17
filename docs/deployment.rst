=====================
Deploy the full stack
=====================

Build and deploy backend and frontend images from the same reviewed revision.
The production Compose file is a single-server example. It binds the frontend
only to loopback and expects an HTTPS reverse proxy in front of it.

Configure the host
==================

Keep deployment secrets outside Git. Supply ``.env`` locally or inject equivalent
environment values through your deployment system. Production requires:

* ``ROLA_SECRET_KEY``: a stable, high-entropy Django signing key.
* ``ROLA_POSTGRESQL_PASSWORD``: the database credential.
* ``ALLOWED_HOSTS``: comma-separated public hostnames without schemes.
* ``ROLA_FRONTEND_URL``: the public HTTPS origin used in account emails.
* ``ROLA_CSRF_TRUSTED_ORIGINS``: trusted HTTPS origins for Django admin.
* ``ROLA_USE_SES=true``, ``ROLA_SES_ACCESS_KEY_ID``,
  ``ROLA_SES_SECRET_ACCESS_KEY`` and ``ROLA_DEFAULT_FROM_EMAIL`` for SMTP delivery.

The SMTP settings retain the existing SES naming. ``ROLA_SMTP_HOST`` and
``ROLA_SMTP_PORT`` can select another SMTP-over-TLS endpoint. Verify sender
configuration and delivery with the actual provider before accepting account
registrations. Development uses the console mail backend; production without
configured delivery uses a disabled backend and fails the deployment check.

The backend redirects HTTP to HTTPS outside debug mode. The production Compose
example trusts the frontend proxy's forwarded protocol. Configure the external
HTTPS proxy to overwrite ``X-Forwarded-Proto`` and forward the public Host
header and discard client-supplied forwarding headers. The example sets
``ROLA_NUM_PROXIES=2`` for the external proxy and frontend Nginx; adjust it to
match your trusted proxy count (zero for direct access). Do not expose the Django container directly to untrusted clients.

For a deployment outside the supplied Compose stack, set
``ROLA_TRUST_PROXY=true`` when a trusted proxy terminates HTTPS. If it replaces
the public Host header, also set ``ROLA_USE_X_FORWARDED_HOST=true`` and have it
supply the original host. Enable these settings only when the proxy overwrites
the corresponding headers and Django cannot be reached directly. Django must
see the public scheme and host to generate valid pagination links; the client
rejects pagination URLs outside the configured API origin.

Keep frontend and API under the same origin when possible. Separate origins
require ``ROLA_CORS_ALLOWED_ORIGINS`` to explicitly list the allowed browser
origins. Secure cookie and CSRF configuration still apply to Django admin.

Initialize a new deployment
===========================

For an empty database:

.. code-block:: console

   docker compose -f compose.production.yaml build
   docker compose -f compose.production.yaml up -d db redis
   docker compose -f compose.production.yaml run --rm backend python manage.py migrate --noinput
   docker compose -f compose.production.yaml run --rm backend python manage.py collectstatic --noinput
   docker compose -f compose.production.yaml run --rm backend python manage.py check --deploy
   docker compose -f compose.production.yaml run --rm backend python manage.py createsuperuser
   docker compose -f compose.production.yaml up -d backend frontend

For an existing database, perform :doc:`upgrading` before ordinary migration.
Compose does not automatically apply production migrations at web-server startup.

Files and object storage
========================

The example shares uploaded media and collected static files with frontend
Nginx using named volumes. Include media in your backup policy. Nginx serves
``/media/`` and ``/static2/`` from these volumes.

To use S3-compatible storage, set ``ROLA_USE_S3=true``,
``ROLA_AWS_MEDIA_STORAGE_BUCKET_NAME`` and
``ROLA_AWS_STATIC_STORAGE_BUCKET_NAME``. Optional settings include
``ROLA_AWS_REGION_NAME``, ``ROLA_AWS_S3_ENDPOINT_URL``,
``ROLA_AWS_ACCESS_KEY_ID`` and ``ROLA_AWS_SECRET_ACCESS_KEY``.
Prefer the provider's workload identity where available. Configure static
bucket delivery and access policy for browser access. Uploaded media uses
signed URLs and does not overwrite existing object names.

Enable backup processing
========================

Set ``ROLA_BACKUP_ENABLED=true`` and the ``ROLA_BACKUP_AWS_*`` bucket and
credential variables in the backend environment. Apply the backup migrations,
then start the worker profile:

.. code-block:: console

   docker compose -f compose.production.yaml run --rm backend python manage.py migrate --noinput
   docker compose -f compose.production.yaml --profile backup up -d backend worker frontend

The worker consumes the ``rolca.backup`` channel. The web process and worker
must use the same database, Redis service, storage configuration and media.
Verify the upload workflow against a non-production bucket before rollout.

Frontend configuration
======================

``VITE_PAYPAL_CLIENT_ID`` is a public client identifier supplied at frontend
build time. Leave it empty if the contest confirmation does not use PayPal.
Changing a production frontend build-time value requires rebuilding the image.

Contest confirmation HTML retains the existing ability to run scripts supplied
by trusted administrators, including payment initialization. Treat permission
to edit that content as permission to execute code in visitors' browsers.
Ordinary contest notices are sanitized separately.

Account recovery
================

Password-reset requests return the same response for known and unknown accounts.
Email delivery is synchronous, so response times can still reveal whether an
active account exists. Per-IP throttling limits repeated requests but does not
eliminate this timing difference. Removing it requires a separate asynchronous
mail-delivery design.

Profile updates
===============

Registration requires a password. Profile PUT and PATCH requests must omit it;
use the change-password endpoint to replace credentials. PUT requires the full
profile and address fields, while PATCH accepts partial updates. The verified
email address is immutable: omit it or supply the existing address. Attempts to
change it return a field validation error without modifying the profile.
