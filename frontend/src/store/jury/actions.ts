import _ from 'lodash';
import { AppState, AppThunk } from '..';
import ContestService from '../../services/ContestService';
import JudgeSubmissionService from '../../services/JudgeSubmissionService';
import { Contest, Submission, Theme } from '../../types/api';
import fetchAll from '../../utils/fetchAll';

import {
  JuryActionTypes,
  PERFORM_INITIALIZE,
  SET_SUBMISSION,
  SET_PREVIOUS_SUBMISSION,
  SET_NEXT_SUBMISSION,
} from './types';

export const performInitialize = (
  contest: Contest,
  theme: Theme,
  submissions: Submission[],
  currentIndex: number,
): JuryActionTypes => ({
  type: PERFORM_INITIALIZE,
  payload: { contest, theme, submissions, currentIndex },
});

export const setSubmission = (submissionId: number): JuryActionTypes => ({
  type: SET_SUBMISSION,
  payload: { submissionId },
});
export const setPreviousSubmission = (): JuryActionTypes => ({
  type: SET_PREVIOUS_SUBMISSION,
});
export const setNextSubmission = (): JuryActionTypes => ({
  type: SET_NEXT_SUBMISSION,
});

export const initializeStore =
  (
    contestId: string,
    themeId: string,
    submissionId: number | undefined,
  ): AppThunk<Promise<void>> =>
  async (dispatch): Promise<void> => {
    const { data: contest } = await ContestService.getContest(contestId);
    const theme = contest.themes.find((t) => t.id.toString() === themeId);

    const submissionResource = () =>
      JudgeSubmissionService.getSubmissionsByTheme(parseInt(themeId, 10));
    const submissions = await fetchAll(submissionResource);

    let currentIndex = 0;
    if (submissionId) {
      currentIndex = _.findIndex(submissions, (s) => s.id === submissionId);
      if (currentIndex === -1) currentIndex = 0;
    }

    if (theme)
      dispatch(performInitialize(contest, theme, submissions, currentIndex));
  };

export const getCurrentSubmission = (state: AppState): Submission | null => {
  const {
    jury: { submissions, currentIndex },
  } = state;

  if (!submissions) return null;
  return submissions[currentIndex] ?? null;
};

export const getIsPrevious = (state: AppState): boolean => {
  const {
    jury: { submissions, currentIndex },
  } = state;

  if (!submissions) return false;
  return currentIndex > 0;
};

export const getIsNext = (state: AppState): boolean => {
  const {
    jury: { submissions, currentIndex },
  } = state;

  if (!submissions) return false;
  return submissions.length > currentIndex + 1;
};
