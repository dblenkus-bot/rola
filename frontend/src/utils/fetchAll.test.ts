import { AxiosHeaders, type AxiosResponse } from 'axios';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import fetchAll from './fetchAll';
import { apiClient } from '../services/Base';
import type { PaginatedResponse } from '../types/api';

vi.mock('../services/Base', () => ({
  apiClient: { defaults: { baseURL: '/api/v1' }, get: vi.fn() },
}));
beforeEach(() => vi.clearAllMocks());
function page(
  results: number[],
  next: string | null,
): AxiosResponse<PaginatedResponse<number>> {
  return {
    data: { results, next, count: 3, previous: null },
    config: { headers: new AxiosHeaders() },
    headers: {},
    status: 200,
    statusText: 'OK',
  };
}
describe('paginated API reads', () => {
  it('loads every page and retains the configured HTTP development origin', async () => {
    vi.mocked(apiClient.get)
      .mockResolvedValueOnce(page([2], '/api/v1/contest?page=3'))
      .mockResolvedValueOnce(page([3], null));
    const result = await fetchAll(() =>
      Promise.resolve(page([1], '/api/v1/contest?page=2')),
    );
    expect(result).toEqual([1, 2, 3]);
    expect(apiClient.get).toHaveBeenNthCalledWith(
      1,
      `${window.location.origin}/api/v1/contest?page=2`,
    );
  });
  it('does not send authenticated pagination requests to another origin', async () => {
    await expect(
      fetchAll(() =>
        Promise.resolve(
          page([1], 'https://other.example/api/v1/contest?page=2'),
        ),
      ),
    ).rejects.toThrow('Invalid pagination URL');
    expect(apiClient.get).not.toHaveBeenCalled();
  });
  it('rejects pagination loops', async () => {
    vi.mocked(apiClient.get).mockResolvedValue(
      page([2], '/api/v1/contest?page=2'),
    );
    await expect(
      fetchAll(() => Promise.resolve(page([1], '/api/v1/contest?page=2'))),
    ).rejects.toThrow('Invalid pagination URL');
    expect(apiClient.get).toHaveBeenCalledTimes(1);
  });
});

it('follows an absolute URL on the configured API origin', async () => {
  vi.mocked(apiClient.get).mockResolvedValueOnce(page([2], null));
  const next = `${window.location.origin}/api/v1/contest?page=2`;
  expect(await fetchAll(() => Promise.resolve(page([1], next)))).toEqual([
    1, 2,
  ]);
  expect(apiClient.get).toHaveBeenCalledWith(next);
});

it('rejects a scheme mismatch instead of rewriting the server URL', async () => {
  const next = new URL('/api/v1/contest?page=2', window.location.origin);
  next.protocol = next.protocol === 'http:' ? 'https:' : 'http:';
  await expect(
    fetchAll(() => Promise.resolve(page([1], next.href))),
  ).rejects.toThrow('Invalid pagination URL');
  expect(apiClient.get).not.toHaveBeenCalled();
});
