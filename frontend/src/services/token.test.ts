import { beforeEach, describe, expect, it } from 'vitest';
import { loadToken, rejectToken } from './token';

beforeEach(() => localStorage.clear());
describe('persisted authentication', () => {
  it('keeps a token until its actual expiry', () => {
    const token = {
      token: 'test-token',
      expires: new Date(Date.now() + 60_000).toISOString(),
    };
    localStorage.setItem('token', JSON.stringify(token));
    expect(loadToken()).toEqual(token);
  });
  it.each([
    'not json',
    '{}',
    JSON.stringify({ token: 123, expires: '2999-01-01' }),
    JSON.stringify({ token: 'expired', expires: '2000-01-01' }),
    JSON.stringify({ token: 'invalid', expires: 'never' }),
  ])('discards invalid or expired credentials: %s', (stored) => {
    localStorage.setItem('token', stored);
    expect(loadToken()).toBeNull();
    expect(localStorage.getItem('token')).toBeNull();
  });
});

it('does not clear a newer login when an older request is rejected', () => {
  const token = { token: 'new-session', expires: '2999-01-01' };
  localStorage.setItem('token', JSON.stringify(token));
  rejectToken('Token old-session');
  expect(loadToken()).toEqual(token);
});
