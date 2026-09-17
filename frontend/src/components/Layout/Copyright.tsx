import React from 'react';

import { Typography } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

const useStyles = makeStyles()({
  copyright: {
    flexGrow: 1,
  },
});

const Copyright: React.FC = () => {
  const { classes } = useStyles();

  return (
    <Typography
      variant="body1"
      color="textSecondary"
      align="center"
      className={classes.copyright}
    >
      {new Date().getFullYear()} - <b>Domen Blenkuš</b>
    </Typography>
  );
};

export default Copyright;
