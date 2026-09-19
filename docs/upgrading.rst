=================================
Migrate an existing Rola database
=================================

The backend starts from fresh initial migrations. The existing deployment
requires a one-off manual data migration; the application does not upgrade
historical schemas automatically.

Create a new database using the setup in :doc:`deployment`, then transfer the
existing data and media. Rehearse the transfer from a restored copy before
switching traffic. Keep the original database and files available for rollback.
Do not apply the new initial migrations directly to the old database or import
its ``django_migrations`` records into the new one.

During the transfer:

* Preserve user primary keys, public UUIDs and relationships between records.
* Map each old contest's ``confirmation_email_id`` to the integration app's
  ``ContestNotification`` record for that contest.
* Leave retired backup tables out of the new database. Stop the old backup
  worker; Redis is no longer required by Rola.

Verify accounts, contests, submissions, payments, judging, email templates and
uploaded media before switching traffic to the new backend and frontend.

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
