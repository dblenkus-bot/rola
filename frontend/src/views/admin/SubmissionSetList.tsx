import { Alert } from '@mui/material';
import { requestError } from '../../services/errors';
import { useParams } from 'react-router-dom';
import React from 'react';
import { AxiosPromise } from 'axios';

import { withStyles } from 'tss-react/mui';

import { Grid, Typography } from '@mui/material';

import ConfirmDialog from '../../components/Notifications/ConfirmDialog';

import { editListStyles } from '../../styles/general';
import SubmissionSetService from '../../services/SubmissionSetService';
import ContestService from '../../services/ContestService';
import { Contest, PaginatedResponse, SubmissionSet } from '../../types/api';
import SubmissionSetTable from '../../components/SubmissionSetTable/SubmissionSetTable';
import LoadingProgress from '../../components/LoadingProgress';
import { WithTranslation, withTranslation } from 'react-i18next';

type StyleProps = {
  classes?: Record<keyof ReturnType<typeof editListStyles>, string>;
};

interface RouteMatchParams {
  contestId: string;
}

interface SubmissionSetListState {
  error: string | null;
  contest: Contest | null;
  pendingSubmissionSet: SubmissionSet | null;
  showDialog: boolean;
}

interface SubmissionSetListProps extends StyleProps, WithTranslation {
  match: { params: RouteMatchParams };
}

class SubmissionSetList extends React.Component<
  SubmissionSetListProps,
  SubmissionSetListState
> {
  constructor(props: SubmissionSetListProps) {
    super(props);

    this.state = {
      error: null,
      contest: null,
      pendingSubmissionSet: null,
      showDialog: false,
    };
  }

  async componentDidMount(): Promise<void> {
    await this.fetchData();
  }

  fetchData = async (): Promise<void> => {
    this.setState({ error: null });
    try {
      const {
        match: {
          params: { contestId },
        },
      } = this.props;

      const { data: contest } = await ContestService.getContest(contestId);

      this.setState({ contest });
    } catch (error) {
      this.setState({ error: requestError(error) });
    }
  };

  handleDelete = (pendingSubmissionSet: SubmissionSet): void => {
    this.setState({ pendingSubmissionSet, showDialog: true });
  };

  closeDialog = (): void =>
    this.setState({ pendingSubmissionSet: null, showDialog: false });

  processDelete = async (): Promise<void> => {
    this.setState({ error: null });
    try {
      const { pendingSubmissionSet } = this.state;
      if (!pendingSubmissionSet) return;

      await SubmissionSetService.deleteSubmissionSet(pendingSubmissionSet.id);
      await this.fetchData();
    } catch (error) {
      this.setState({ error: requestError(error) });
    }
  };

  render(): React.ReactNode {
    if (this.state.error)
      return <Alert severity="error">{this.state.error}</Alert>;
    const { contest, showDialog } = this.state;
    const { t } = this.props;

    if (!contest) return <LoadingProgress />;

    const dataSource = (
      page: number,
      pageSize: number,
    ): AxiosPromise<PaginatedResponse<SubmissionSet>> =>
      SubmissionSetService.getByContest(contest.id.toString(), page, pageSize);

    return (
      <>
        <Typography align="center" variant="h2">
          {contest?.title}
        </Typography>

        <Grid size={{ xs: 12 }}>
          <SubmissionSetTable
            contestId={contest ? contest.id : 0}
            dataSource={dataSource}
            onDelete={this.handleDelete}
          />
        </Grid>

        <ConfirmDialog
          open={showDialog}
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

const RoutedView = withTranslation()(
  withStyles(SubmissionSetList, editListStyles),
);
export default function RouteView() {
  const params = useParams();
  const contestId = params.contestId;
  if (!contestId) {
    throw new Error('Missing contestId route parameter');
  }
  return <RoutedView match={{ params: { contestId } }} />;
}
