import { range } from 'lodash';

import { ThemeModel } from '../../types/models';

import { submissionInit } from './actions';
import { THEME_INIT, UploadActionTypes } from './types';
import submissionReducer from './reducerSubmission';
import { getEmptyTheme } from './utils';

const initialState = getEmptyTheme();

const reducer = (
  state = initialState,
  action: UploadActionTypes,
): ThemeModel => {
  switch (action.type) {
    case THEME_INIT: {
      const {
        id,
        is_series: isSeries = false,
        n_photos: imageNumber,
        title,
      } = action.payload;
      const submissionNumber = isSeries ? 1 : imageNumber;
      const submissionMeta = {
        imageNumber: isSeries ? imageNumber : 1,
        isSeries: isSeries ?? false,
        isNew: true,
        isChanged: false,
        titleRequired: false,
        descriptionRequired: false,
      };
      return {
        ...state,
        meta: {
          ...state.meta,
          id,
          title,
        },
        submissions: range(submissionNumber).map((id) =>
          submissionReducer(
            undefined,
            submissionInit({ ...submissionMeta, id }),
          ),
        ),
      };
    }
    default: {
      if ('submission_id' in action) {
        const submissions = state.submissions.map((submission) => {
          return submission.meta.id === action.submission_id
            ? submissionReducer(submission, action)
            : submission;
        });
        return { ...state, submissions };
      }
      return state;
    }
  }
};

export default reducer;
