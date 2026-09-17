import type { components } from '../types/generated-api';
import { AxiosPromise } from 'axios';

import { PaginatedResponse, Submission } from '../types/api';

import { apiClient } from './Base';

export type SubmissionCreatePayload =
  components['schemas']['SubmissionRequest'];

export default {
  createSubmissions(
    submissions: SubmissionCreatePayload[],
  ): AxiosPromise<Submission[]> {
    return apiClient.post('/submission', submissions);
  },
  deleteSubmission(submissionsId: number): AxiosPromise<Submission[]> {
    return apiClient.delete(`/submission/${submissionsId}`);
  },
  getSubmissionsByContest(
    contentId: number,
  ): AxiosPromise<PaginatedResponse<Submission>> {
    return apiClient.get('/submission', { params: { contest: contentId } });
  },
  getSubmissionsByTheme(
    themeId: number,
  ): AxiosPromise<PaginatedResponse<Submission>> {
    return apiClient.get('/submission', { params: { theme: themeId } });
  },
};
