import { createRoot } from 'react-dom/client';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import * as Sentry from '@sentry/react';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import './i18n/config';
import App from './App';

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({ dsn: import.meta.env.VITE_SENTRY_DSN });
}
const root = document.getElementById('root');
if (!root) {
  throw new Error('Application root is missing');
}
createRoot(root).render(
  <ThemeProvider theme={createTheme()}>
    <App />
  </ThemeProvider>,
);
