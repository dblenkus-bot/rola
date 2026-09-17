import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'react-router-dom';

import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
} from '@mui/material';

import ContestService from '../../services/ContestService';
import { Contest } from '../../types/api';
import LoadingProgress from '../../components/LoadingProgress';

interface RouteMatchParams {
  contestId: string;
}

const SelectTheme: React.FC = () => {
  const [contest, setContest] = useState<null | Contest>(null);
  const { contestId } = useParams<keyof RouteMatchParams>();
  if (!contestId) {
    throw new Error('Missing contestId route parameter');
  }

  const { t } = useTranslation();

  useEffect(() => {
    const fetchContest = async (): Promise<void> => {
      const { data } = await ContestService.getContest(contestId);
      setContest(data);
    };
    fetchContest();
  }, [contestId]);

  if (!contest) return <LoadingProgress />;

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableBody>
          <TableRow>
            <TableCell colSpan={3}>
              <b>{contest.title}</b>
            </TableCell>
          </TableRow>
          {contest.themes.map((theme) => (
            <TableRow key={theme.id}>
              <TableCell padding="checkbox" />
              <TableCell>{theme.title}</TableCell>
              <TableCell align="right">
                <Button
                  to={`/results/contest/${contest.id}/theme/${theme.id}`}
                  component={Link}
                  color="primary"
                >
                  {t('view')}
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default SelectTheme;
