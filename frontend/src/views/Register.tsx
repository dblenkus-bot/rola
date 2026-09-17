import type { InputChange } from '../types/models';
import { formErrors } from '../services/errors';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { Link as RouterLink } from 'react-router-dom';

import { Card, CardContent, CardHeader, Grid, Link } from '@mui/material';

import RegisterForm, { Errors, Fields } from '../components/Auth/RegisterForm';
import RegisterConfirm from '../components/Auth/RegisterConfirm';

import UserService from '../services/UserService';

type RegisterViewProps = WithTranslation;

interface RegisterViewState {
  fields: Fields;
  errors: Errors;
  done: boolean;
}

class RegisterView extends React.Component<
  RegisterViewProps,
  RegisterViewState
> {
  state = {
    fields: {
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      address: '',
      city: '',
      postal_code: '',
      country: '',
    },
    errors: {
      first_name: null,
      last_name: null,
      email: null,
      password: null,
      address: null,
      city: null,
      postal_code: null,
      country: null,
      non_field_errors: null,
    },
    done: false,
  };

  handleChange = ({ name, value }: InputChange): void => {
    this.setState((state) => {
      const fields: Fields = Object.assign({}, state.fields);
      const errors: Errors = Object.assign({}, state.errors);
      fields[name] = value;
      errors[name] = null;
      errors.non_field_errors = null;
      return { fields, errors };
    });
  };

  handleSubmit = async (): Promise<void> => {
    const { fields } = this.state;
    try {
      await UserService.register(fields);
      this.setState({ done: true });
    } catch (error) {
      this.setState({ errors: { ...this.state.errors, ...formErrors(error) } });
    }
  };

  render() {
    const { errors, done, fields } = this.state;
    const { t } = this.props;

    return (
      <Grid container sx={{ justifyContent: 'center' }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardHeader
              title={t('register')}
              slotProps={{ title: { align: 'center' } }}
            />
            <CardContent>
              {done ? (
                <RegisterConfirm email={fields.email} />
              ) : (
                <>
                  <RegisterForm
                    fields={fields}
                    errors={errors}
                    onChange={this.handleChange}
                    onSubmit={this.handleSubmit}
                  />
                  <Grid container sx={{ justifyContent: 'flex-end' }}>
                    <Grid>
                      <Link component={RouterLink} to="/login" variant="body2">
                        {t('already_have_account')}
                      </Link>
                    </Grid>
                  </Grid>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }
}

export default withTranslation()(RegisterView);
