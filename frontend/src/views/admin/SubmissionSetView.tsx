import { Alert } from '@mui/material';
import { requestError } from '../../services/errors';
import { useParams } from 'react-router-dom';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { Card, Grid } from '@mui/material';

import { Contest, SubmissionSet } from '../../types/api';

import SubmissionSetService from '../../services/SubmissionSetService';
import ContestService from '../../services/ContestService';

interface RouteMatchParams {
  contestId: string;
  submissionSetId: string;
}

interface SubmissionListProps extends WithTranslation {
  match: { params: RouteMatchParams };
}

interface SubmissionListState {
  error: string | null;
  contest: Contest | null;
  submissionSet: SubmissionSet | null;
}

class SubmissionList extends React.Component<
  SubmissionListProps,
  SubmissionListState
> {
  constructor(props: SubmissionListProps) {
    super(props);

    this.state = {
      error: null,
      contest: null,
      submissionSet: null,
    };
  }

  async componentDidMount(): Promise<void> {
    await this.fetchData();
  }

  getSubmissionSetAuthor = (submissionSet: SubmissionSet): string => {
    if (!submissionSet.submissions[0]) return '';

    const {
      first_name: firstName,
      last_name: lastName,
      email,
    } = submissionSet.submissions[0].author;
    return `${firstName} ${lastName}, ${email}`;
  };

  async fetchData(): Promise<void> {
    this.setState({ error: null });
    try {
      const {
        match: {
          params: { contestId, submissionSetId },
        },
      } = this.props;

      const { data: contest } = await ContestService.getContest(contestId);
      const { data: submissionSet } =
        await SubmissionSetService.getSubmissionSet(submissionSetId);
      this.setState({ contest, submissionSet });
    } catch (error) {
      this.setState({ error: requestError(error) });
    }
  }

  render(): React.ReactNode {
    if (this.state.error)
      return <Alert severity="error">{this.state.error}</Alert>;
    const { contest, submissionSet } = this.state;
    const { t } = this.props;

    return (
      <>
        <Grid size={{ xs: 12 }}>
          <b>{t('contest')}:</b> {contest?.title}
          <br />
          <b>{t('author')}:</b>{' '}
          {submissionSet ? this.getSubmissionSetAuthor(submissionSet) : ''}
          <br />
          <br />
        </Grid>
        <Grid container spacing={2}>
          {submissionSet?.submissions.map((submission) => {
            const theme = contest?.themes.find(
              (t) => t.id === submission.theme,
            );
            return (
              <Grid key={submission.id} size={{ xs: 12, sm: 6, md: 4 }}>
                <Card raised>
                  {(submission.files ?? []).map((file) => (
                    <img
                      key={file.id}
                      alt={submission.title ?? ''}
                      src={file.file}
                      style={{
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        maxHeight: '100%',
                        padding: '5px',
                        width: '100%',
                      }}
                    />
                  ))}
                  <br />
                  <b>{t('title')}:</b> {submission.title}
                  <br />
                  <b>{t('theme')}:</b> {theme?.title}
                  {submission.description && (
                    <>
                      <br />
                      <b>{t('description')}:</b> {submission.description}
                    </>
                  )}
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </>
    );
  }
}

const RoutedView = withTranslation()(SubmissionList);
export default function RouteView() {
  const params = useParams();
  const contestId = params.contestId;
  if (!contestId) {
    throw new Error('Missing contestId route parameter');
  }
  const submissionSetId = params.submissionSetId;
  if (!submissionSetId) {
    throw new Error('Missing submissionSetId route parameter');
  }
  return <RoutedView match={{ params: { contestId, submissionSetId } }} />;
}
