import { Alert } from '@mui/material';
import { requestError } from '../../services/errors';
import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import {
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
} from '@mui/material';

import JudgeContestService from '../../services/JudgeContestService';
import { JuryContest } from '../../types/api';

const SelectTheme: React.FC = () => {
  const [contests, setContests] = useState<JuryContest[]>([]);
  const { t } = useTranslation();

  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContests = async (): Promise<void> => {
      const { data } = await JudgeContestService.getContests();
      setContests(data.results);
    };
    fetchContests().catch((error: unknown) => setError(requestError(error)));
  }, []);

  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableBody>
          {contests.map((contest) => (
            <React.Fragment key={contest.id}>
              <TableRow>
                <TableCell colSpan={4}>
                  <b>{contest.title}</b>
                </TableCell>
              </TableRow>
              {contest.themes.map((theme) => (
                <TableRow key={theme.id}>
                  <TableCell padding="checkbox" />
                  <TableCell>{theme.title}</TableCell>
                  <TableCell>
                    {theme.ratings_number}/{theme.submissions_number}
                  </TableCell>
                  <TableCell align="right">
                    <Button
                      to={`/judge/contest/${contest.id}/theme/${theme.id}`}
                      component={Link}
                      color="primary"
                    >
                      {t('open')}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default SelectTheme;
