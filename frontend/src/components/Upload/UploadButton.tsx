import React from 'react';

import { makeStyles } from 'tss-react/mui';

import { Link } from 'react-router-dom';

import { Button, Grid } from '@mui/material';

interface UploadButtonProps {
  contestId: number;
}

const useStyles = makeStyles()(({ spacing }) => ({
  button: {
    margin: spacing(2),
    padding: spacing(2, 4),
  },
  link: {
    textDecoration: 'none',
  },
}));

const UploadButton: React.FC<UploadButtonProps> = ({ contestId }) => {
  const { classes } = useStyles();

  return (
    <Grid container sx={{ justifyContent: 'center' }}>
      <Link to={`/contest/${contestId}/upload`} className={classes.link}>
        <Button
          className={classes.button}
          color="primary"
          size="large"
          variant="contained"
        >
          Upload Photos
        </Button>
      </Link>
    </Grid>
  );
};

export default UploadButton;
