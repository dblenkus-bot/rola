import type { InputChange } from '../../types/models';
import React from 'react';

import { useTranslation } from 'react-i18next';

import { Button } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import InputField from '../Upload/InputField';

import { authStyles } from '../../styles/general';

export interface Fields {
  email: string;
  [key: string]: string;
}

interface PasswordResetRequestFormProps {
  fields: Fields;
  onChange: (event: InputChange) => void;
  onSubmit: () => Promise<void>;
}

const useStyles = makeStyles()(authStyles);

const PasswordResetRequestForm: React.FC<PasswordResetRequestFormProps> = (
  props,
) => {
  const { classes } = useStyles();
  const { t } = useTranslation();

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    props.onSubmit();
  };

  return (
    <form onSubmit={handleSubmit}>
      <InputField
        name="email"
        label={t('email')}
        value={props.fields.email}
        autoComplete="email"
        autoFocus
        required
        onChange={props.onChange}
      />
      <Button
        type="submit"
        fullWidth
        variant="contained"
        color="primary"
        className={classes.submit}
      >
        {t('send_reset_link')}
      </Button>
    </form>
  );
};

export default PasswordResetRequestForm;
