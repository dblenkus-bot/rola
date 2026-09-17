import type { InputChange } from '../../types/models';
import React from 'react';

import { useTranslation } from 'react-i18next';

import { Button, Grid } from '@mui/material';
import { Alert } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import InputField from '../Upload/InputField';

import { authStyles } from '../../styles/general';

export interface Fields {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  [key: string]: string;
}

export interface Errors {
  first_name: null | Array<string>;
  last_name: null | Array<string>;
  email: null | Array<string>;
  password: null | Array<string>;
  address: null | Array<string>;
  city: null | Array<string>;
  postal_code: null | Array<string>;
  country: null | Array<string>;
  non_field_errors: null | Array<string>;
  [key: string]: string[] | null;
}

interface RegisterFormProps {
  fields: Fields;
  errors: Errors;
  onChange: (event: InputChange) => void;
  onSubmit: () => Promise<void>;
}

const useStyles = makeStyles()(authStyles);

const RegisterForm: React.FC<RegisterFormProps> = (props) => {
  const { classes } = useStyles();
  const { t } = useTranslation();
  const { errors, fields, onChange, onSubmit } = props;

  const getError = (field: string): string | null => {
    return errors[field]?.join(' ') ?? null;
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit}>
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <InputField
            name="first_name"
            label={t('first_name')}
            value={fields.first_name}
            error={getError('first_name')}
            autoComplete="given-name"
            autoFocus
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <InputField
            name="last_name"
            label={t('last_name')}
            value={fields.last_name}
            error={getError('last_name')}
            autoComplete="family-name"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="email"
            label={t('email')}
            value={fields.email}
            error={getError('email')}
            autoComplete="email"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="password"
            label={t('password')}
            value={fields.password}
            error={getError('password')}
            autoComplete="new-password"
            type="password"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="address"
            label={t('address')}
            value={fields.address}
            error={getError('address')}
            autoComplete="street-address"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="city"
            label={t('city')}
            value={fields.city}
            error={getError('city')}
            autoComplete="address-level2"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="postal_code"
            label={t('postal_code')}
            value={fields.postal_code}
            error={getError('postal_code')}
            autoComplete="postal-code"
            required
            onChange={onChange}
          />
        </Grid>
        <Grid size={{ xs: 12 }}>
          <InputField
            name="country"
            label={t('country')}
            value={fields.country}
            error={getError('country')}
            autoComplete="country-name"
            required
            onChange={onChange}
          />
        </Grid>
      </Grid>
      {getError('non_field_errors') !== null ? (
        <Alert severity="error" className={classes.alert}>
          {getError('non_field_errors')}
        </Alert>
      ) : (
        false
      )}
      <Button
        type="submit"
        fullWidth
        variant="contained"
        color="primary"
        className={classes.submit}
      >
        {t('register')}
      </Button>
    </form>
  );
};

export default RegisterForm;
