import { requestError } from './errors';
import { AxiosPromise } from 'axios';
import { useEffect, useState } from 'react';

import { BaseResource, PaginatedResponse } from '../types/api';

interface PaginationProps<R> {
  source: (
    page: number,
    pageSize: number,
  ) => AxiosPromise<PaginatedResponse<R>>;
}

interface PaginationReturn<R> {
  error: string | null;
  isLoading: boolean;
  data: R[];
  count: number;
  page: number;
  pageSize: number;
  changePage: (pageNumber: number) => void;
  changePageSize: (newPageSize: number) => void;
}

function usePagination<R extends BaseResource>({
  source,
}: PaginationProps<R>): PaginationReturn<R> {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setLoading] = useState(true);
  const [data, setData] = useState<R[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);

  useEffect(() => {
    let active = true;
    setError(null);
    setLoading(true);
    source(page, pageSize)
      .then(({ data }) => {
        if (active) {
          setData(data.results);
          setCount(data.count);
        }
      })
      .catch((error: unknown) => {
        if (active) setError(requestError(error));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [source, page, pageSize]);

  const changePage = (pageNumber: number): void => setPage(pageNumber);

  const changePageSize = (newPageSize: number): void => {
    setPageSize(newPageSize);
    setPage(1);
  };

  return {
    error,
    isLoading,
    data,
    count,
    page,
    pageSize,
    changePage,
    changePageSize,
  };
}

export default usePagination;
