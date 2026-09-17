import type { AxiosPromise } from 'axios';
import type { PaginatedResponse } from '../types/api';
import { apiClient } from '../services/Base';

export default async function fetchAll<T>(
  resource: () => AxiosPromise<PaginatedResponse<T>>,
): Promise<T[]> {
  let response = await resource();
  const result = [...response.data.results];
  const base = new URL(
    apiClient.defaults.baseURL || '/api/v1',
    window.location.origin,
  );
  const visited = new Set<string>();
  while (response.data.next) {
    const next = new URL(response.data.next, base);
    if (
      next.origin !== base.origin ||
      !next.pathname.startsWith(`${base.pathname}/`) ||
      visited.has(next.href)
    ) {
      throw new Error('Invalid pagination URL.');
    }
    visited.add(next.href);
    response = await apiClient.get<PaginatedResponse<T>>(next.href);
    result.push(...response.data.results);
  }
  return result;
}
