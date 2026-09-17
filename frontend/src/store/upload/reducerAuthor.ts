import { AuthorModel } from '../../types/models';
import { AUTHOR_UPDATE, UploadActionTypes } from './types';
import { getEmptyAuthor } from './utils';

const initialSate = getEmptyAuthor();

const reducer = (
  state = initialSate,
  action: UploadActionTypes,
): AuthorModel => {
  switch (action.type) {
    case AUTHOR_UPDATE: {
      const { name, value } = action.payload;
      return {
        ...state,
        [name]: value,
      };
    }
    default: {
      return state;
    }
  }
};

export default reducer;
