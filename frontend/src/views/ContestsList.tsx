import { useEffect, useState } from 'react';
import { Alert, Grid, Typography } from '@mui/material';
import ContestCard from '../components/Upload/ContestCard';
import LoadingProgress from '../components/LoadingProgress';
import ContestService from '../services/ContestService';
import type { Contest } from '../types/api';
import fetchAll from '../utils/fetchAll';

export default function ContestsListView() {
  const [contests, setContests] = useState<Contest[] | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let active = true;
    fetchAll(ContestService.getActiveContests)
      .then((data) => {
        if (active) {
          setContests(data);
        }
      })
      .catch(() => {
        if (active) {
          setFailed(true);
        }
      });
    return () => {
      active = false;
    };
  }, []);
  if (failed) {
    return (
      <Alert severity="error">Could not load contests. Please try again.</Alert>
    );
  }
  if (!contests) {
    return <LoadingProgress />;
  }
  if (!contests.length) {
    return <Typography>No active contests.</Typography>;
  }
  return (
    <Grid container spacing={2}>
      {contests.map((contest) => (
        <Grid key={contest.id} size={{ xs: 12, sm: 6, md: 4 }}>
          <ContestCard contest={contest} />
        </Grid>
      ))}
    </Grid>
  );
}
