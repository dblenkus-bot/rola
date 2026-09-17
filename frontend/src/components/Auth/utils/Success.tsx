import React from 'react';

import { Button, Typography } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { authStyles } from '../../../styles/general';

interface RegisterActivateSuccessProps {
  title: string;
  buttonText: string;
  onClick: () => void;
}

const useStyles = makeStyles()(authStyles);

const RegisterActivateSuccess: React.FC<RegisterActivateSuccessProps> = (
  props,
) => {
  const { classes } = useStyles();
  const { buttonText, title, onClick } = props;

  return (
    <>
      <Typography component="h3" variant="h6">
        {title}
      </Typography>
      <Button
        type="submit"
        fullWidth
        variant="contained"
        color="primary"
        className={classes.submit}
        onClick={() => onClick()}
      >
        {buttonText}
      </Button>
    </>
  );
};

export default RegisterActivateSuccess;
