import React from 'react';

import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { authStyles } from '../../styles/general';

const useStyles = makeStyles()(authStyles);

const RegisterActivateFailed: React.FC = () => {
  const { classes } = useStyles();
  const { t } = useTranslation();

  return (
    <>
      <Typography component="h3" variant="h6">
        {t('activation_failed')}
      </Typography>
      <Typography className={classes.paragraph}>
        {t('invalid_token')}
      </Typography>
    </>
  );
};

export default RegisterActivateFailed;
