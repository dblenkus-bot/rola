import { useContext } from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import AuthProvider, { userContext } from './AuthProvider';
import PrivateRoute from './PrivateRoute';
import UserService from '../../services/UserService';

vi.mock('../../services/UserService', () => ({ default: { login: vi.fn() } }));
beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});
function Session() {
  const auth = useContext(userContext);
  return (
    <>
      <span>{auth.isLoggedIn() ? 'Signed in' : 'Signed out'}</span>
      <button
        onClick={() =>
          auth.login({ email: 'user@example.com', password: 'example' })
        }
      >
        Log in
      </button>
      <button onClick={auth.logout}>Log out</button>
    </>
  );
}
function Destination() {
  const location = useLocation();
  return <p>{location.state?.from?.pathname}</p>;
}
describe('authentication flows', () => {
  it('stores a login and clears it on logout', async () => {
    const token = { token: 'example-token', expires: '2999-01-01T00:00:00Z' };
    vi.mocked(UserService.login).mockResolvedValue({ data: token } as Awaited<
      ReturnType<typeof UserService.login>
    >);
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <Session />
      </AuthProvider>,
    );
    await user.click(screen.getByRole('button', { name: 'Log in' }));
    await screen.findByText('Signed in');
    expect(JSON.parse(localStorage.getItem('token') || 'null')).toEqual(token);
    await user.click(screen.getByRole('button', { name: 'Log out' }));
    expect(screen.getByText('Signed out')).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
  });
  it('preserves the requested path when redirecting to login', async () => {
    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/contest/1/upload']}>
          <Routes>
            <Route
              path="/contest/:id/upload"
              element={
                <PrivateRoute>
                  <p>Private content</p>
                </PrivateRoute>
              }
            />
            <Route path="/login" element={<Destination />} />
          </Routes>
        </MemoryRouter>
      </AuthProvider>,
    );
    await waitFor(() =>
      expect(screen.getByText('/contest/1/upload')).toBeInTheDocument(),
    );
    expect(screen.queryByText('Private content')).not.toBeInTheDocument();
  });
});
