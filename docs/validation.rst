=====================
Validation boundaries
=====================

The repository's CI workflow is the executable definition of routine checks.
It validates the Django host and domain apps together, tests the frontend,
checks the generated API contract and builds separate production images.
See :doc:`contributing` for the same commands locally.

Database and integration coverage
=================================

The backend suite covers account permissions, registration and recovery,
submission validation and ownership, judging, published results, payment
updates, exports and media processing. Integration tests use PostgreSQL for the
host and a separate configuration using Django's standard user model without
``drf_user``.

Both backend configurations initialize their test databases from the current
initial migrations. CI also checks for model changes missing a migration.

Frontend component tests cover user-visible authentication, API failure
handling and content behavior.

Deployment validation
=====================

Automated tests do not establish that an existing production database or an
external provider is configured correctly. Rehearse the manual data transfer in
:doc:`upgrading` using a restored database and media copy. Verify SMTP, object storage and payment
configuration with the deployment's actual providers before switching traffic.

The test fixtures contain synthetic data. No production database, user accounts,
email provider or payment transaction is used for repository validation.
