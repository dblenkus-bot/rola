import { useContext, type ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { userContext } from './AuthProvider';

export default function PrivateRoute({ children }: { children: ReactNode }) {
  const user = useContext(userContext);
  const location = useLocation();
  return user.isLoggedIn() ? (
    children
  ) : (
    <Navigate to="/login" state={{ from: location }} replace />
  );
}
