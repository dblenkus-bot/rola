import {
  AuthorModel,
  ContestModel,
  ImageModel,
  SubmissionModel,
  ThemeModel,
} from '../types/models';

import imageReader from './imageReader';
import { anyImage, countImages } from './image';
import { asyncMap } from './async';

interface BaseError {
  hasError: boolean;
}

interface BaseObject {
  errors: BaseError;
}

const hasError = (obj: BaseObject | BaseObject[]): boolean => {
  if (Array.isArray(obj)) {
    return obj.some((o) => o.errors.hasError);
  } else {
    return obj.errors.hasError;
  }
};

const validateImage = async (image: ImageModel): Promise<ImageModel> => {
  const constructResponse = (fileError: string | null): ImageModel => ({
    ...image,
    errors: { file: fileError, hasError: !!fileError },
  });

  const { file } = image;
  if (file) {
    if (file === undefined) {
      return constructResponse('Please select an image.');
    }
    if (file.type !== 'image/jpeg') {
      return constructResponse('File must be in JPEG format.');
    }
    if (file.size > 5 * 1024 ** 2) {
      return constructResponse('Image must be smaller than 5MB.');
    }

    let img: HTMLImageElement;
    try {
      img = await imageReader(file);
    } catch {
      return constructResponse('Invalid file.');
    }

    if (img.height < 2500 && img.width < 2500)
      return constructResponse('Long edge should be at least 2500px.');

    if (img.height > 3500 || img.width > 3500)
      return constructResponse('Longe edge should not exceed 3500px.');
  }

  return constructResponse(null);
};

const validateSubmission = async (
  submission: SubmissionModel,
): Promise<SubmissionModel> => {
  const { title, description } = submission;
  const { titleRequired, descriptionRequired, isSeries } = submission.meta;
  const images = await asyncMap(submission.images, validateImage);

  if ((title || description) && !anyImage(images) && images[0]) {
    images[0].errors.file = 'Please select an image';
    images[0].errors.hasError = true;
  }

  if (isSeries && anyImage(images) && countImages(images) < 2 && images[0]) {
    images[0].errors.file = 'Series must contain at least 2 images';
    images[0].errors.hasError = true;
  }

  const errors = {
    description:
      descriptionRequired && !description ? 'Please enter description.' : null,
    title: titleRequired && !title ? 'Please enter title.' : null,
    hasError:
      hasError(images) ||
      (descriptionRequired && !description) ||
      (titleRequired && !title),
  };

  return { meta: submission.meta, title, description, images, errors };
};

const validateTheme = async (theme: ThemeModel): Promise<ThemeModel> => {
  const submissions = await asyncMap(theme.submissions, validateSubmission);
  const errors = { hasError: hasError(submissions) };

  return { meta: theme.meta, submissions, errors };
};

const validateAuthor = (
  author: AuthorModel,
  initial: boolean,
  contest: ContestModel,
): AuthorModel => {
  const { first_name, last_name, dob, school } = author;

  const errors = {
    first_name: !first_name && !initial ? 'Please enter the first name.' : null,
    last_name: !last_name && !initial ? 'Please enter the last name.' : null,
    dob:
      contest.meta.dobRequired && !dob && !initial
        ? 'Please enter the date of birth.'
        : null,
    school:
      contest.meta.schoolRequired && !school && !initial
        ? 'Please enter the school.'
        : null,
    mentor: null,
    club: null,
    distinction: null,
    hasError:
      !initial &&
      (!first_name ||
        !last_name ||
        (contest.meta.dobRequired && !dob) ||
        (contest.meta.schoolRequired && !school)),
  };

  return { ...author, errors };
};

export default async (
  contest: ContestModel,
  initial = false,
): Promise<ContestModel> => {
  const author = validateAuthor(contest.author, initial, contest);
  const themes = await asyncMap(contest.themes, validateTheme);
  const errors = { hasError: hasError(themes) || hasError(author) };

  return { meta: contest.meta, author, themes, errors };
};
