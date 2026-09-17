import { Contest as ApiContest } from '../../types/api';

export const STORE_CONTESTS = 'STORE_CONTESTS';

export type Contest = ApiContest;

export type ContestsState = Array<Contest>;

type StoreContestsAction = {
  type: typeof STORE_CONTESTS;
  payload: {
    contests: Contest[];
  };
};

export type ContestsActionTypes = StoreContestsAction;
