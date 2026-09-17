============
Architecture
============

Rola is one product with a Django backend and a React frontend. A single
repository lets an API change and its client update be reviewed together.
The backend and frontend retain independent dependency manifests and images.

Backend boundaries
==================

The ``rola`` package selects the database, authentication, storage, email and
URL configuration. ``drf_user`` implements the current account API. Rolca's
``core``, ``rating``, ``payment`` and ``backup`` apps contain domain behavior.

Rolca relates to the user selected by ``AUTH_USER_MODEL``. Host-specific
notification configuration and user profile lookups live in
``rola_integration``. A different Django project can provide different
integration callables and a different user model without installing
``drf_user``. See :doc:`integrations` for that contract.

The optional backup worker is a separate process using the same backend code
and database. Redis supplies the Channels transport. Enabling it requires both
the backup app and a running worker; starting the web server alone does not
process backup messages.

Frontend boundary
=================

The browser uses the host's ``/api/v1`` endpoints. Request code stays in
``frontend/src/services``. The backend publishes an OpenAPI schema, and the
frontend generates TypeScript definitions from it. CI regenerates both outputs
to detect drift. Generated types supplement runtime validation and API tests.

The frontend remains a client-rendered React application. Vite supplies the
local development server and production build. Production serves the built
assets through Nginx. Neither frontend deployment mode requires moving Django
business logic into JavaScript.

Repository history
==================

The original Rolca history, including its reviewed modernization branch, and
the frontend history are parents of the import commits in Rola. Directory moves
preserve Python import paths and Django app labels. Original database table and
user identities remain significant during upgrades; repository layout does not
reset migration history.
