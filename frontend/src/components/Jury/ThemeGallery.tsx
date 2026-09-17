import React from 'react';
import { Card, Grid } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { Rating as RatingModel, Submission } from '../../types/api';
import Rating from './Rating';

interface ThemeGalleryProps {
  submissions: Submission[];
  isSeries: boolean;
  ratings: RatingModel[];
  handleClick: (submissionId: number) => void;
}

const ThemeGallery: React.FC<ThemeGalleryProps> = ({
  submissions,
  isSeries,
  ratings,
  handleClick,
}: ThemeGalleryProps) => {
  const useStyles = makeStyles()({
    card: { cursor: 'pointer' },
    wrapOut: {
      width: '100%',
      paddingBottom: isSeries ? '10%' : '100%',
      position: 'relative',
    },
    wrapIn: {
      position: 'absolute',
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minWidth: '0',
    },
    image: {
      maxHeight: '100%',
      maxWidth: '100%',
      padding: '5px',
    },
    title: { textAlign: 'center' },
    rating: { textAlign: 'center' },
  });

  const { classes } = useStyles();

  return (
    <Grid container spacing={2}>
      {submissions.map(({ id, files, title }) => {
        const rating = ratings.find((r) => r.submission === id);
        return isSeries ? (
          <Grid key={id} size={{ xs: 12 }}>
            <Card
              raised
              className={classes.card}
              onClick={() => handleClick(id)}
            >
              <div className={classes.wrapOut}>
                <div className={classes.wrapIn}>
                  {files.map((file) => (
                    <img
                      key={file.id}
                      className={classes.image}
                      src={file.thumbnail || file.file}
                      alt={title ?? ''}
                    />
                  ))}
                </div>
              </div>
              <div className={classes.title}>
                <b>{title}</b>
              </div>
              <div className={classes.rating}>
                <Rating
                  max={10}
                  value={rating?.rating || 0}
                  size="small"
                  disabled
                />
              </div>
            </Card>
          </Grid>
        ) : (
          <Grid key={id} size={{ xs: 6, sm: 4, md: 3, lg: 3 }}>
            <Card
              raised
              className={classes.card}
              onClick={() => handleClick(id)}
            >
              <div className={classes.wrapOut}>
                <div className={classes.wrapIn}>
                  {files.map((file) => (
                    <img
                      key={file.id}
                      className={classes.image}
                      src={file.thumbnail || file.file}
                      alt={title ?? ''}
                    />
                  ))}
                </div>
              </div>
              <div className={classes.title}>
                <b>{title}</b>
              </div>
              <div className={classes.rating}>
                <Rating
                  max={10}
                  value={rating?.rating || 0}
                  size="small"
                  disabled
                />
              </div>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
};

export default ThemeGallery;
