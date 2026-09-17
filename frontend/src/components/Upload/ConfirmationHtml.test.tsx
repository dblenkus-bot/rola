import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import ConfirmationHtml from './ConfirmationHtml';

afterEach(() => {
  vi.unstubAllEnvs();
  document
    .querySelectorAll('script[src^="https://www.paypal.com/sdk/js"]')
    .forEach((script) => script.remove());
});

it('retries the payment SDK after an earlier load failed', async () => {
  vi.stubEnv('VITE_PAYPAL_CLIENT_ID', 'test-client');
  const first = render(<ConfirmationHtml html="<p>First confirmation</p>" />);
  const failed = document.querySelector(
    'script[src^="https://www.paypal.com/sdk/js"]',
  );
  expect(failed).not.toBeNull();
  fireEvent.error(failed!);
  expect(
    await screen.findByText('Payment provider could not be loaded.'),
  ).toBeInTheDocument();
  first.unmount();
  render(<ConfirmationHtml html="<p>Second confirmation</p>" />);
  const retry = document.querySelector(
    'script[src^="https://www.paypal.com/sdk/js"]',
  );
  expect(retry).not.toBeNull();
  expect(retry).not.toBe(failed);
  fireEvent.load(retry!);
  await waitFor(() =>
    expect(screen.getByText('Second confirmation')).toBeInTheDocument(),
  );
});
