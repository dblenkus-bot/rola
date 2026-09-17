import axios from 'axios';
import store from '../store';
import { addNotificationError } from '../store/notifications/actions';
import { loadToken, rejectToken } from './token';

export const apiClient = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL || ''}/api/v1`,
  headers: { Accept: 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = loadToken();
  if (token) {
    config.headers.set('Authorization', `Token ${token.token}`);
  }
  return config;
});
apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      rejectToken(error.config?.headers.get('Authorization'));
    }
    if (
      !axios.isAxiosError(error) ||
      !error.response ||
      error.response.status >= 500
    ) {
      store.dispatch(addNotificationError('Network error occurred.'));
    }
    return Promise.reject(error);
  },
);
