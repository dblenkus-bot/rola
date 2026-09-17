import type { AppThunk } from '..';

import { STORE_CONTESTS, Contest, ContestsActionTypes } from './types';

import ContestService from '../../services/ContestService';

export const storeContests = (contests: Contest[]): ContestsActionTypes => ({
  type: STORE_CONTESTS,
  payload: { contests },
});

export const loadContests = (): AppThunk<Promise<void>> => async (dispatch) => {
  const resp = await ContestService.getActiveContests();
  dispatch(storeContests(resp.data.results));
};
