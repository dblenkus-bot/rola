import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AxiosError } from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';
import { apiClient } from './services/Base';
import { contest } from './test/fixtures';
import './i18n/config';
import App from './App';
import store from './store';
import { deleteMessage } from './store/notifications/actions';

function response(config: InternalAxiosRequestConfig, data: unknown) {
  return { config, data, status: 200, statusText: 'OK', headers: {} };
}
beforeEach(() => {
  localStorage.clear();
  for (const notification of store.getState().notifications) {
    store.dispatch(deleteMessage(notification.id));
  }
  apiClient.defaults.adapter = async (config) => {
    if (config.url === '/contest') {
      return response(config, {
        results: [contest],
        count: 1,
        next: null,
        previous: null,
      });
    }
    if (config.url === '/contest/1') {
      return response(config, { ...contest, dob_required: true });
    }
    if (config.url === '/user/login') {
      return response(config, {
        token: 'signed-in',
        expires: '2999-01-01T00:00:00Z',
      });
    }
    if (
      config.url === '/user/activate_account' ||
      config.url === '/user/password_reset'
    ) {
      return response(config, {});
    }
    throw new Error(`Unexpected request: ${config.url}`);
  };
});
function open(path: string) {
  window.history.replaceState(null, '', path);
  render(<App />);
}
describe('application routes', () => {
  it('loads the public contest list through the API', async () => {
    open('/contests');
    expect(
      await screen.findByRole('heading', { name: contest.title }),
    ).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Open' })).toHaveAttribute(
      'href',
      '/contest/1/upload',
    );
  });
  it('shows a useful empty state', async () => {
    apiClient.defaults.adapter = async (config) =>
      response(config, { results: [], count: 0, next: null, previous: null });
    open('/contests');
    expect(await screen.findByText('No active contests.')).toBeInTheDocument();
  });
  it('shows a failed list request', async () => {
    apiClient.defaults.adapter = async () => {
      throw new Error('Offline');
    };
    open('/contests');
    expect(
      await screen.findByText('Could not load contests. Please try again.'),
    ).toBeInTheDocument();
  });

});

describe('failed page requests', () => {
  it.each([
    '/contest/1/upload',
    '/contest/1/confirm',
    '/user/submissions',
    '/judge',
    '/judge/contest/1/theme/1',
    '/judge/contest/1/theme/1/rate',
    '/judge/contest/1/theme/1/overview',
    '/admin/contest/1/submissions',
    '/admin/contest/1/submission/1',
    '/results/contest/1',
    '/results/contest/1/theme/1',
    '/results/contest/1/theme/1/submission/1',
  ])(
    'shows a permission error instead of a loading screen at %s',
    async (path) => {
      localStorage.setItem(
        'token',
        JSON.stringify({ token: 'signed-in', expires: '2999-01-01T00:00:00Z' }),
      );
      apiClient.defaults.adapter = async (config) => {
        throw new AxiosError(
          'Forbidden',
          'ERR_BAD_REQUEST',
          config,
          undefined,
          {
            ...response(config, { detail: 'Forbidden' }),
            status: 403,
          },
        );
      };
      open(path);
      expect(
        await screen.findByText(
          'You do not have permission to perform this action.',
          {},
          { timeout: 5000 },
        ),
      ).toBeInTheDocument();
      expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
    },
  );

  it('shows pagination failures after the contest loads', async () => {
    localStorage.setItem(
      'token',
      JSON.stringify({ token: 'signed-in', expires: '2999-01-01T00:00:00Z' }),
    );
    apiClient.defaults.adapter = async (config) => {
      if (config.url === '/contest/1') return response(config, contest);
      throw new AxiosError('Forbidden', 'ERR_BAD_REQUEST', config, undefined, {
        ...response(config, {}),
        status: 403,
      });
    };
    open('/admin/contest/1/submissions');
    expect(
      await screen.findByText(
        'You do not have permission to perform this action.',
      ),
    ).toBeInTheDocument();
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });

  it('redirects a revoked session to login and removes its credentials', async () => {
    localStorage.setItem(
      'token',
      JSON.stringify({ token: 'revoked', expires: '2999-01-01T00:00:00Z' }),
    );
    apiClient.defaults.adapter = async (config) => {
      throw new AxiosError(
        'Unauthorized',
        'ERR_BAD_REQUEST',
        config,
        undefined,
        {
          ...response(config, {}),
          status: 401,
        },
      );
    };
    open('/contest/1/upload');
    expect(
      await screen.findByRole('textbox', { name: /email/i }),
    ).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
    expect(window.location.pathname).toBe('/login');
  });

  it('rejects a missing reset token without sending a request', async () => {
    const adapter = vi.fn();
    apiClient.defaults.adapter = adapter;
    open('/password-reset');
    const user = userEvent.setup();
    await user.type(
      await screen.findByLabelText(/new password/i),
      'Replacement!73',
    );
    await user.click(
      screen.getByRole('button', { name: /reset password|password reset/i }),
    );
    expect(
      await screen.findByText('Invalid password reset token.'),
    ).toBeInTheDocument();
    expect(adapter).not.toHaveBeenCalled();
  });
});
