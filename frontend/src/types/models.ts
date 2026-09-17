export interface InputChange {
  name: string;
  value: string;
}

export interface DateChange {
  name: string;
  value: Date;
}

export interface FileChange {
  file: File;
  url: string;
}

export interface ImageError {
  hasError: boolean;
  file: string | null;
}

export interface ImageMeta {
  id: number;
  isChanged: boolean;
  isNew: boolean;
}

export interface ImageModel {
  meta: ImageMeta;
  file: File | undefined;
  url: string;
  errors: ImageError;
}

export interface SubmissionError {
  hasError: boolean;
  title: string | null;
  description: string | null;
}

export interface SubmissionMeta {
  id: number;
  imageNumber: number;
  isChanged: boolean;
  isNew: boolean;
  isSeries: boolean;
  titleRequired: boolean;
  descriptionRequired: boolean;
}

export interface SubmissionModel {
  meta: SubmissionMeta;
  title: string;
  description: string;
  images: ImageModel[];
  errors: SubmissionError;
}

export interface ThemeError {
  hasError: boolean;
}

export interface ThemeMeta {
  id: number;
  title: string;
}

export interface ThemeModel {
  meta: ThemeMeta;
  submissions: SubmissionModel[];
  errors: ThemeError;
}

export interface AuthorError {
  hasError: boolean;
  first_name: string | null;
  last_name: string | null;
  dob: string | null;
  school: string | null;
  mentor: string | null;
  club: string | null;
  distinction: string | null;
}

export interface AuthorModel {
  first_name: string;
  last_name: string;
  dob: Date | undefined;
  school?: string;
  mentor?: string;
  club?: string;
  distinction: string;
  errors: AuthorError;
}

export interface ContestError {
  hasError: boolean;
}

export interface ContestMeta {
  title: string;
  description: string;
  noticeHtml: string;
  headerImage: string | null;
  dobRequired: boolean;
  clubShow: boolean;
  clubRequired: boolean;
  schoolShow: boolean;
  schoolRequired: boolean;
}

export interface ContestModel {
  meta: ContestMeta;
  author: AuthorModel;
  themes: ThemeModel[];
  errors: ContestError;
}
