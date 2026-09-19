==========================
Configure a different host
==========================

Rolca's domain apps can run with a different Django user model and without
``drf_user`` in ``INSTALLED_APPS``. The Rola host supplies its own account and
notification integration; a different host supplies the configuration below.

User identity
=============

Set Django's ``AUTH_USER_MODEL`` before creating a new database. Rolca uses
ordinary foreign keys to that model. The user must satisfy Django and DRF's
authentication and permission interfaces. Changing an existing deployment's
user model still requires a separate schema and data migration.

Confirmation delivery
=====================

``ROLCA_SUBMISSION_CONFIRMATION_CALLBACK`` is the dotted import path of a
callable accepting one saved ``SubmissionSet``. Rolca schedules it after the
submission transaction commits. A rollback does not send a confirmation.
Without a configured callback, submission confirmations are disabled.

Rola configures:

.. code-block:: python

   ROLCA_SUBMISSION_CONFIRMATION_CALLBACK = (
       "rola_integration.hooks.send_submission_confirmation"
   )

The host's ``ContestNotification`` model links a contest to ``drf_user.Email``.
Its Django admin inline retains per-contest template selection. This association
belongs to the integration app, so another host can use another template model
or delivery service without adding that model to Rolca.

The callback receives committed data and must not assume delivery is part of
the database transaction. Callback failures are logged; they do not undo the
submission. If guaranteed delivery is required, the host should provide a
persistent delivery mechanism with its own retry policy.

Author country
==============

``ROLCA_AUTHOR_COUNTRY_CALLBACK`` is a dotted callable path accepting an
``Author`` and returning a country string or ``None``. Without a callback, the
results API returns ``null`` for the country.

``ROLCA_AUTHOR_SELECT_RELATED`` contains single-valued relationship paths
relative to the author. Use it to preload any relationships read by the
callback. Rola configures:

.. code-block:: python

   ROLCA_AUTHOR_COUNTRY_CALLBACK = "rola_integration.hooks.get_author_country"
   ROLCA_AUTHOR_SELECT_RELATED = ("user__location",)

The result queries always preload the author's user. A host whose user model
has no location relationship leaves the additional paths empty. Changing only
the callback while retaining an invalid relationship path is not sufficient.

Migration ownership
===================

Each app has an initial migration for its current models. Domain migrations
reference ``AUTH_USER_MODEL``. A different host can initialize an empty database
without installing ``drf_user`` or ``rola_integration``.

Existing Rola data is transferred manually as described in :doc:`upgrading`.
