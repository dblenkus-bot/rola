import { range } from 'lodash';

import { SubmissionModel } from '../../types/models';

import { imageInit } from './actions';
import { SUBMISSION_INIT, SUBMISSION_UPDATE, UploadActionTypes } from './types';
import imageReducer from './reducerImage';
import { getEmptySubmission } from './utils';

interface RequiredFields {
  titleRequired?: boolean;
  descriptionRequired?: boolean;
}

const initialSate = getEmptySubmission();

const reducer = (
  state = initialSate,
  action: UploadActionTypes,
): SubmissionModel => {
  switch (action.type) {
    case SUBMISSION_INIT: {
      const { imageNumber } = action.payload;
      const imageMeta = {
        isNew: true,
        isChanged: false,
      };
      return {
        ...state,
        meta: action.payload,
        images: range(imageNumber).map((image_id) =>
          imageReducer(undefined, imageInit({ ...imageMeta, id: image_id })),
        ),
      };
    }
    case SUBMISSION_UPDATE: {
      const { name, value } = action.payload;
      const { isSeries } = state.meta;

      const requiredFields: RequiredFields = {};
      if (name === 'title' || name === 'description') {
        requiredFields.titleRequired = !!value;
        requiredFields.descriptionRequired = isSeries && !!value;
      }

      return {
        ...state,
        meta: { ...state.meta, ...requiredFields, isChanged: true },
        [name]: value,
      };
    }
    default: {
      if ('image_id' in action) {
        const { description, meta, title } = state;
        const images = state.images.map((image) => {
          return image.meta.id === action.image_id
            ? imageReducer(image, action)
            : image;
        });

        const anyImage = images.some((image) => !!image.file);
        const titleRequired = anyImage || (meta.isSeries && !!description);
        const descriptionRequired = meta.isSeries && (anyImage || !!title);

        return {
          ...state,
          meta: { ...state.meta, titleRequired, descriptionRequired },
          images,
        };
      }
      return state;
    }
  }
};

export default reducer;
