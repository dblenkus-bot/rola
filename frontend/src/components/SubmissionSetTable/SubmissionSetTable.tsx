import React, { useCallback, useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { AxiosPromise } from 'axios';
import _ from 'lodash';

import {
  LabelDisplayedRowsArgs,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableFooter,
  TableHead,
  TablePagination,
  TableRow,
} from '@mui/material';

import { PaginatedResponse, Payment, SubmissionSet } from '../../types/api';
import SubmissionSetTableRow from './SubmissionSetTableRow';
import usePagination from '../../services/usePagination';
import PaymentService from '../../services/PaymentService';

interface SubmissionSetTableProps {
  contestId: number;
  dataSource: (
    page: number,
    pageSize: number,
  ) => AxiosPromise<PaginatedResponse<SubmissionSet>>;
  onDelete: (submissionSet: SubmissionSet) => void;
}

const SubmissionSetTable: React.FC<SubmissionSetTableProps> = ({
  contestId,
  dataSource,
  onDelete,
}: SubmissionSetTableProps) => {
  const [payments, setPayments] = useState<Payment[]>([]);
  const {
    data: submissionSets,
    count,
    page,
    pageSize,
    changePage,
    changePageSize,
  } = usePagination<SubmissionSet>({ source: dataSource });
  const { t } = useTranslation();

  const fetchPayments = useCallback(async (): Promise<void> => {
    if (submissionSets.length === 0) {
      setPayments([]);
      return;
    }

    const submissionSetIds = _.map(submissionSets, 'id');
    const { data } = await PaymentService.getBySubmissionSets(submissionSetIds);
    setPayments(data.results);
  }, [submissionSets]);

  useEffect(() => {
    fetchPayments();
  }, [fetchPayments]);

  const handlePageChange = (
    event: React.MouseEvent<HTMLButtonElement> | null,
    newPage: number,
  ): void => {
    changePage(newPage + 1);
  };

  const handleChangeRowsPerPage = (
    event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ): void => {
    changePageSize(parseInt(event.target.value, 10));
  };

  const handlePaidChange = async (
    submissionSetId: number,
    paid: boolean,
  ): Promise<void> => {
    await PaymentService.updatePayment(submissionSetId, paid);
    await fetchPayments();
  };

  const getLabelDisplayedRows = ({
    from,
    to,
    count: total,
  }: LabelDisplayedRowsArgs): React.ReactNode => {
    return t('displayed_rows', { from, to, total });
  };

  return (
    <>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>{t('name')}</TableCell>
              <TableCell>{t('submited')}</TableCell>
              <TableCell>{t('n_themes')}</TableCell>
              <TableCell>{t('n_submissions')}</TableCell>
              <TableCell>{t('paid')}</TableCell>
              <TableCell />
            </TableRow>
          </TableHead>
          <TableBody>
            {submissionSets.map((submissionSet) => {
              const payment = _.find(
                payments,
                (p) => p.submissionset === submissionSet.id,
              );
              return (
                <SubmissionSetTableRow
                  key={submissionSet.id}
                  contestId={contestId}
                  submissionSet={submissionSet}
                  payment={payment}
                  onPaidChange={handlePaidChange}
                  onDelete={onDelete}
                />
              );
            })}
          </TableBody>
          <TableFooter>
            <TableRow>
              <TablePagination
                rowsPerPageOptions={[1, 20, 50, 100]}
                count={count}
                rowsPerPage={pageSize}
                page={page - 1}
                onPageChange={handlePageChange}
                onRowsPerPageChange={handleChangeRowsPerPage}
                labelRowsPerPage={t('rows_per_page')}
                labelDisplayedRows={getLabelDisplayedRows}
              />
            </TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
    </>
  );
};

export default SubmissionSetTable;
