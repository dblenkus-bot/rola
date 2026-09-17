import React, { ReactNode } from 'react';

import { Typography } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { authStyles } from '../../../styles/general';

interface RegisterConfirmProps {
  title: string;
  children: ReactNode;
}

const useStyles = makeStyles()(authStyles);

const RegisterConfirm: React.FC<RegisterConfirmProps> = (props) => {
  const { classes } = useStyles();
  const { title, children } = props;

  return (
    <>
      <Typography component="h3" variant="h6">
        {title}
      </Typography>
      <Typography className={classes.paragraph}>{children}</Typography>
    </>
  );
};

export default RegisterConfirm;
