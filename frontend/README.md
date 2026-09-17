# Rolca frontend

Run the frontend from this directory using the Node version in `.node-version`:

```sh
npm ci
npm run dev
```

Vite proxies backend requests to `http://localhost:8000`. Set `API_PROXY_TARGET`
when the Django server runs elsewhere. The repository's Compose setup configures
this for you.

Check changes with:

```sh
npm run lint
npm run format:check
npm run typecheck
npm test
npm run build
```

Build output is written to `dist/`. The production Docker image serves it through
Nginx and forwards API requests to the backend.

Regenerate the API types after updating `backend/openapi.yaml`:

```sh
npm run api:generate
```

The generated file is consumed by the API services and excluded from manual
formatting. Commit the schema and generated types together.

Optional public build settings are `VITE_API_BASE_URL`, `VITE_SENTRY_DSN`, and
`VITE_PAYPAL_CLIENT_ID`. Rebuild the frontend after changing them. Only put public
values in Vite settings.

Contest notices are sanitized. Contest confirmation templates retain executable
HTML for existing payment integrations, so only trusted administrators should be
allowed to edit them. If a template uses PayPal, supply its public client ID when
building the frontend; the SDK loads before the template runs.
