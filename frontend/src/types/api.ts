import type { components } from './generated-api';

type Schemas = components['schemas'];
export interface PaginatedResponse<R> {
  count: number;
  results: R[];
  next: string | null;
  previous: string | null;
}
export type BaseResource = Pick<
  Schemas['Author'],
  'id' | 'created' | 'modified'
>;
export type Image = Schemas['File'];
export type Institution = Schemas['Institution'];
export type Author = Schemas['Author'];
export type ResultsAuthor = Schemas['AuthorResults'];
export type Submission = Schemas['Submission'];
export type ResultsSubmission = Schemas['SubmissionResults'];
export type SubmissionSet = Schemas['SubmissionSet'];
export type Theme = Schemas['Theme'];
export type JuryTheme = Schemas['JudgeTheme'];
export type ResultsTheme = Schemas['ThemeResults'];
export type Contest = Schemas['Contest'];
export type JuryContest = Schemas['JudgeContest'];
export type Payment = Schemas['Payment'];
export type Rating = Schemas['Rating'];
