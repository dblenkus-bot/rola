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
updates, exports, media processing and backup behavior. Integration tests use
PostgreSQL for the host and a separate configuration using Django's standard
user model without ``drf_user``.

Migration tests start from the preserved historical graph, retain user and
contest data, copy confirmation-template associations, adopt the portable
baselines and verify rerunning the upgrade. They also exercise rejection of
unknown histories and incomplete baseline adoption.

The Redis transport check runs against a real Redis instance when
``ROLCA_REDIS_URL`` is configured. S3 behavior is tested with a fake external
service boundary. Frontend component tests cover user-visible authentication,
API failure handling and content behavior.

Deployment validation
=====================

Automated tests do not establish that an existing production database or an
external provider is configured correctly. Rehearse :doc:`upgrading` against a
restored database and media copy. Verify SMTP, object storage, payment
configuration and background processing with the deployment's actual providers
before switching traffic.

The test fixtures contain synthetic data. No production database, user accounts,
email provider or payment transaction is used for repository validation.
