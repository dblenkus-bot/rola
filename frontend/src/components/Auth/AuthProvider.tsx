import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import UserService, { type LoginPayload } from '../../services/UserService';
import {
  loadToken,
  sessionChanged,
  type AuthToken,
} from '../../services/token';

interface AuthContext {
  user: AuthToken | null;
  login: (payload: LoginPayload) => Promise<void>;
  logout: () => void;
  isLoggedIn: () => boolean;
}

export const userContext = createContext<AuthContext>({
  user: null,
  login: async () => {
    throw new Error('AuthProvider is missing');
  },
  logout: () => {
    throw new Error('AuthProvider is missing');
  },
  isLoggedIn: () => false,
});

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState(loadToken);
  useEffect(() => {
    const refreshSession = () => setUser(loadToken());
    window.addEventListener(sessionChanged, refreshSession);
    window.addEventListener('storage', refreshSession);
    return () => {
      window.removeEventListener(sessionChanged, refreshSession);
      window.removeEventListener('storage', refreshSession);
    };
  }, []);
  const login = useCallback(async (payload: LoginPayload) => {
    const { data } = await UserService.login(payload);
    localStorage.setItem('token', JSON.stringify(data));
    setUser(data);
  }, []);
  const logout = useCallback(() => {
    localStorage.removeItem('token');
    setUser(null);
  }, []);
  const value = useMemo(
    () => ({
      user,
      login,
      logout,
      isLoggedIn: () => user !== null && Date.parse(user.expires) > Date.now(),
    }),
    [user, login, logout],
  );
  return <userContext.Provider value={value}>{children}</userContext.Provider>;
}
