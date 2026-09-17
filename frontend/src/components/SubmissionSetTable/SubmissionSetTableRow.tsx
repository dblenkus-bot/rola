import React from 'react';
import _ from 'lodash';
import { Link } from 'react-router-dom';

import { useTranslation } from 'react-i18next';

import { Button, Checkbox, TableCell, TableRow } from '@mui/material';
import { makeStyles } from 'tss-react/mui';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import MoneyOffIcon from '@mui/icons-material/MoneyOff';

import { editListStyles } from '../../styles/general';
import { Payment, SubmissionSet } from '../../types/api';

interface SubmissionSetTableRowProps {
  contestId: number;
  submissionSet: SubmissionSet;
  payment: Payment | undefined;
  onPaidChange: (submissionSetId: number, paid: boolean) => void;
  onDelete: (submissionSet: SubmissionSet) => void;
}

const getSubmissionSetAuthor = (submissionSet: SubmissionSet): string => {
  const { first_name: firstName, last_name: lastName } = submissionSet.author;
  return `${firstName} ${lastName}`;
};

const getViewLink = (
  contestId: number,
  submissionSet: SubmissionSet,
): string => {
  return `/admin/contest/${contestId}/submission/${submissionSet.id}`;
};

const useStyles = makeStyles()(editListStyles);

const SubmissionSetTableRow: React.FC<SubmissionSetTableRowProps> = ({
  contestId,
  submissionSet,
  payment,
  onPaidChange,
  onDelete,
}: SubmissionSetTableRowProps) => {
  const { classes } = useStyles();
  const { t } = useTranslation();

  const handlePaidChange = (
    event: React.ChangeEvent<HTMLInputElement>,
  ): void => {
    onPaidChange(submissionSet.id, event.target.checked);
  };

  const themeNumber = _(submissionSet.submissions).groupBy('theme').size();

  return (
    <TableRow>
      <TableCell component="th" scope="row">
        {getSubmissionSetAuthor(submissionSet)}
      </TableCell>
      <TableCell>{new Date(submissionSet.created).toLocaleString()}</TableCell>
      <TableCell>{themeNumber}</TableCell>
      <TableCell>{submissionSet.submissions.length}</TableCell>
      <TableCell>
        <Checkbox
          checked={!!payment && payment.paid}
          icon={<MoneyOffIcon color="secondary" />}
          checkedIcon={<AttachMoneyIcon color="primary" />}
          onChange={handlePaidChange}
        />
      </TableCell>
      <TableCell align="right">
        <Button
          component={Link}
          to={getViewLink(contestId, submissionSet)}
          className={classes.button}
          color="primary"
        >
          {t('view')}
        </Button>
        <Button
          variant="text"
          className={classes.button}
          color="secondary"
          onClick={(): void => {
            onDelete(submissionSet);
          }}
        >
          {t('delete')}
        </Button>
      </TableCell>
    </TableRow>
  );
};

export default SubmissionSetTableRow;
