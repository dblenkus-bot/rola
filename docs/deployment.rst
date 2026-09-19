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

Keep frontend and API under the same origin when possible. Separate origins
require ``ROLA_CORS_ALLOWED_ORIGINS`` to explicitly list the allowed browser
origins. Secure cookie and CSRF configuration still apply to Django admin.

Initialize a new deployment
===========================

For an empty database:

.. code-block:: console

   docker compose -f compose.production.yaml build
   docker compose -f compose.production.yaml up -d db
   docker compose -f compose.production.yaml run --rm backend python manage.py migrate --noinput
   docker compose -f compose.production.yaml run --rm backend python manage.py createcachetable
   docker compose -f compose.production.yaml run --rm backend python manage.py collectstatic --noinput
   docker compose -f compose.production.yaml run --rm backend python manage.py check --deploy
   docker compose -f compose.production.yaml run --rm backend python manage.py createsuperuser
   docker compose -f compose.production.yaml up -d backend frontend

For an existing deployment, follow the manual data transfer in :doc:`upgrading`.
Compose does not automatically apply production migrations at web-server startup.

The backend image runs ``gunicorn --bind 0.0.0.0:8000 rola.wsgi:application``.
Sessions use Django's database session backend. The shared throttle cache uses
the ``rola_cache`` table created by ``createcachetable``; initialize it before
starting the backend.

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

Frontend configuration
======================

``VITE_PAYPAL_CLIENT_ID`` is a public client identifier supplied at frontend
build time. Leave it empty if the contest confirmation does not use PayPal.
Changing a production frontend build-time value requires rebuilding the image.

Contest confirmation HTML retains the existing ability to run scripts supplied
by trusted administrators, including payment initialization. Treat permission
to edit that content as permission to execute code in visitors' browsers.
Ordinary contest notices are sanitized separately.
