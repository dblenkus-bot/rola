import type { components } from '../types/generated-api';
import { AxiosPromise } from 'axios';

import { apiClient } from './Base';
import { Author } from '../types/api';

type UserCreatePayload = components['schemas']['AuthorRequest'];

export default {
  create(user: UserCreatePayload): AxiosPromise<Author> {
    const payload = Object.fromEntries(
      Object.entries(user).filter(
        ([, value]) => value !== '' && value !== undefined,
      ),
    );
    return apiClient.post('/author', payload);
  },
};
