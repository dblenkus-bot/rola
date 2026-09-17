import React from 'react';

import { groupBy, sum } from 'lodash';

import { WithTranslation, withTranslation } from 'react-i18next';
import { withStyles } from 'tss-react/mui';

import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Typography,
} from '@mui/material';

import ConfirmDialog from '../components/Notifications/ConfirmDialog';

import { editListStyles } from '../styles/general';
import ContestService from '../services/ContestService';
import SubmissionService from '../services/SubmissionService';
import { Author, Contest, Submission } from '../types/api';
import { asyncMap } from '../utils/async';

type StyleProps = {
  classes?: Record<keyof ReturnType<typeof editListStyles>, string>;
};

interface EditSubmissionListProps extends StyleProps, WithTranslation {}

interface EditSubmissionsListState {
  contests: Contest[];
  submissions: Submission[];
  showDialog: boolean;
  pendingSubmissions: Submission[];
}

interface GroupedSubmissions {
  contest: Contest;
  author: Author;
  submissions: Submission[];
  submissions_n: number;
  photos_n: number;
}

class EditSubmissionsList extends React.Component<
  EditSubmissionListProps,
  EditSubmissionsListState
> {
  state: EditSubmissionsListState = {
    contests: [],
    submissions: [],
    showDialog: false,
    pendingSubmissions: [],
  };

  async fetchSubmissions() {
    const getContestSubmissions = async (contest: Contest) => {
      const submissionsResp = await SubmissionService.getSubmissionsByContest(
        contest.id,
      );
      return submissionsResp.data.results;
    };

    const contests = (await ContestService.getActiveContests()).data.results;
    const submissions = (
      await asyncMap(contests, getContestSubmissions)
    ).flat();

    this.setState({ contests, submissions });
  }

  async componentDidMount() {
    await this.fetchSubmissions();
  }

  getSubmissionsForContest = (contest: Contest): Submission[] => {
    const themeIds = contest.themes.map((theme) => theme.id);
    return this.state.submissions.filter((submission) =>
      themeIds.includes(submission.theme),
    );
  };

  openDialog = (pendingSubmissions: Submission[]) => () => {
    this.setState({ showDialog: true, pendingSubmissions });
  };

  closeDialog = () => this.setState({ showDialog: false });

  processDelete = async () => {
    await asyncMap(this.state.pendingSubmissions, (submission) =>
      SubmissionService.deleteSubmission(submission.id),
    );
    this.fetchSubmissions();
  };

  render() {
    const { t } = this.props;
    const classes = withStyles.getClasses(this.props);

    if (!this.state.submissions.length)
      return (
        <Typography align="center" variant="h3">
          You don't have any active submission to edit.
        </Typography>
      );

    const groupedSubmissions: GroupedSubmissions[] = [];
    this.state.contests.forEach((contest) => {
      const contestSubmissions = this.getSubmissionsForContest(contest);
      const submissionsByAuthor = groupBy(contestSubmissions, 'author.id');

      for (const submissions of Object.values(submissionsByAuthor)) {
        const author = submissions[0]?.author;
        if (!author) {
          continue;
        }
        const submissions_n = Object.keys(groupBy(submissions, 'theme')).length;
        const photos_n = sum(
          submissions.map((submission) => submission.files.length),
        );

        groupedSubmissions.push({
          contest,
          author,
          submissions,
          submissions_n,
          photos_n,
        });
      }
    });

    return (
      <>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t('contest')}</TableCell>
                <TableCell>{t('author')}</TableCell>
                <TableCell>{t('n_themes')}</TableCell>
                <TableCell>{t('n_photos')}</TableCell>
                <TableCell></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {groupedSubmissions.map((group) => (
                <TableRow key={`${group.contest.id}-${group.author.id}`}>
                  <TableCell>{group.contest.title}</TableCell>
                  <TableCell>
                    {`${group.author.first_name} ${group.author.last_name}`}
                  </TableCell>
                  <TableCell>{group.submissions_n}</TableCell>
                  <TableCell>{group.photos_n}</TableCell>
                  <TableCell align="right">
                    <Tooltip title="Not jet available." placement="top">
                      <span>
                        <Button
                          variant="text"
                          className={classes.button}
                          disabled
                        >
                          {t('edit')}
                        </Button>
                      </span>
                    </Tooltip>
                    <Button
                      variant="text"
                      className={classes.button}
                      color="secondary"
                      onClick={this.openDialog(group.submissions)}
                    >
                      {t('delete')}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <ConfirmDialog
          open={this.state.showDialog}
          title={t('delete_confirmation_title')}
          onClose={this.closeDialog}
          onConfirm={this.processDelete}
        >
          {t('delete_confirmation') as React.ReactNode}
        </ConfirmDialog>
      </>
    );
  }
}

export default withTranslation()(
  withStyles(EditSubmissionsList, editListStyles),
);
