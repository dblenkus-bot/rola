import type { components } from '../types/generated-api';
import { AxiosPromise } from 'axios';

import { apiClient } from './Base';
import type { AuthToken } from './token';

type Schemas = components['schemas'];
export type LoginPayload = Schemas['LoginRequest'];
export type RegisterPayload = Schemas['UserRequest'];
export type ActivateUserPayload = Schemas['ActivationRequest'];
export type RequestPasswordResetPayload =
  Schemas['RequestPasswordResetRequest'];
export type PasswordResetPayload = Schemas['PasswordResetRequest'];

export default {
  login(payload: LoginPayload): AxiosPromise<AuthToken> {
    return apiClient.post('/user/login', payload);
  },
  register(payload: RegisterPayload): AxiosPromise {
    return apiClient.post('/user', payload);
  },
  activateUser(payload: ActivateUserPayload): AxiosPromise {
    return apiClient.post('/user/activate_account', payload);
  },
  requestPasswordReset(payload: RequestPasswordResetPayload): AxiosPromise {
    return apiClient.post('/user/request_password_reset', payload);
  },
  passwordReset(payload: PasswordResetPayload): AxiosPromise {
    return apiClient.post('/user/password_reset', payload);
  },
};
