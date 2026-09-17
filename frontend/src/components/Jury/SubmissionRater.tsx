import React from 'react';

import { useTranslation } from 'react-i18next';

import { IconButton } from '@mui/material';
import { makeStyles } from 'tss-react/mui';
import { Close, NavigateBefore, NavigateNext } from '@mui/icons-material';

import { Submission } from '../../types/api';
import Rating from './Rating';

interface SubmissionRaterProps {
  submission: Submission;
  rating: number;
  isSeries: boolean;
  isPrevious: boolean;
  isNext: boolean;
  close: () => void;
  previousSubmission: () => void;
  nextSubmission: () => void;
  updateRating: (value: number) => void;
}

const SubmissionRater: React.FC<SubmissionRaterProps> = ({
  submission,
  rating,
  isSeries,
  isPrevious,
  isNext,
  close,
  previousSubmission,
  nextSubmission,
  updateRating,
}: SubmissionRaterProps) => {
  const useStyles = makeStyles()({
    mainFlex: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    },
    imageFlex: {
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
    },
    image: {
      maxWidth: isSeries ? '30%' : '100%',
      margin: isSeries ? '5px' : '0',
      maxHeight: isSeries ? '40vh' : '80vh',
      flexShrink: 1,
    },
    iconsFlex: {
      alignSelf: 'stretch',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
    },
    invisibleIcon: { visibility: 'hidden' },
    textFlex: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
    },
  });

  const { classes } = useStyles();
  const { t } = useTranslation();
  const { description, files, title } = submission;

  return (
    <div className={classes.mainFlex}>
      <div className={classes.imageFlex}>
        <IconButton disabled={!isPrevious} onClick={() => previousSubmission()}>
          <NavigateBefore />
        </IconButton>
        <div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {files.slice(0, 3).map((file) => (
              <img
                className={classes.image}
                src={file.file}
                alt={title ?? ''}
              />
            ))}
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {files.slice(3, 6).map((file) => (
              <img
                className={classes.image}
                src={file.file}
                alt={title ?? ''}
              />
            ))}
          </div>
        </div>
        <div className={classes.iconsFlex}>
          <IconButton onClick={() => close()}>
            <Close />
          </IconButton>
          <IconButton disabled={!isNext} onClick={() => nextSubmission()}>
            <NavigateNext />
          </IconButton>

          <IconButton className={classes.invisibleIcon}>
            <Close />
          </IconButton>
        </div>
      </div>

      <div className={classes.textFlex}>
        <div>
          <b>{t('title')}:</b> {title}
        </div>
        <b>{t('description')}:</b>
        {description}
      </div>
      <div>
        <Rating
          max={10}
          value={rating}
          onChange={(value) => updateRating(value)}
        />
      </div>
    </div>
  );
};

export default SubmissionRater;
