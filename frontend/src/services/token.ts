import type { components } from '../types/generated-api';
export type AuthToken = components['schemas']['Token'];

export function loadToken(): AuthToken | null {
  const stored = localStorage.getItem('token');
  if (!stored) {
    return null;
  }
  try {
    const value: unknown = JSON.parse(stored);
    if (
      typeof value === 'object' &&
      value !== null &&
      'token' in value &&
      typeof value.token === 'string' &&
      value.token &&
      'expires' in value &&
      typeof value.expires === 'string' &&
      Date.parse(value.expires) > Date.now()
    ) {
      return { token: value.token, expires: value.expires };
    }
  } catch {
    /* Invalid persisted credentials must not prevent startup. */
  }
  localStorage.removeItem('token');
  return null;
}

export const sessionChanged = 'rola:session-changed';

export function rejectToken(authorization: unknown): void {
  const current = loadToken();
  if (current && authorization === `Token ${current.token}`) {
    localStorage.removeItem('token');
    window.dispatchEvent(new Event(sessionChanged));
  }
}
