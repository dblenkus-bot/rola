import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Alert, Typography } from '@mui/material';
import ContestService from '../services/ContestService';
import type { Contest } from '../types/api';
import HeaderImage from '../components/Layout/HeaderImage';
import NoticeHtml from '../components/Upload/NoticeHtml';
import UploadButton from '../components/Upload/UploadButton';
import LoadingProgress from '../components/LoadingProgress';

export default function ContestDetails() {
  const { contestId } = useParams();
  const [contest, setContest] = useState<Contest | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    if (!contestId) {
      return;
    }
    let active = true;
    setContest(null);
    setFailed(false);
    ContestService.getContest(contestId)
      .then(({ data }) => {
        if (active) {
          setContest(data);
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
  }, [contestId]);
  if (failed || !contestId) {
    return <Alert severity="error">Could not load this contest.</Alert>;
  }
  if (!contest) {
    return <LoadingProgress />;
  }
  return (
    <>
      {contest.header_image ? (
        <HeaderImage src={contest.header_image} />
      ) : (
        <Typography align="center" variant="h2">
          {contest.title}
        </Typography>
      )}
      <UploadButton contestId={contest.id} />
      <NoticeHtml notice={contest.notice_html ?? ''} />
      <UploadButton contestId={contest.id} />
    </>
  );
}
