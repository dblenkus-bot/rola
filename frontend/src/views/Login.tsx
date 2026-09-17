import type { InputChange } from '../types/models';
import { formErrors } from '../services/errors';
import { useLocation, type Location } from 'react-router-dom';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { Link as RouterLink, Navigate } from 'react-router-dom';

import { Card, CardContent, CardHeader, Grid, Link } from '@mui/material';

import { userContext } from '../components/Auth/AuthProvider';
import LoginForm, { Errors, Fields } from '../components/Auth/LoginForm';

interface LoginViewProps extends WithTranslation {
  location: Location;
}

interface LoginViewState {
  fields: Fields;
  errors: Errors;
  redirect: boolean;
}

interface LocationState {
  from?: { pathname: string };
}

class LoginView extends React.Component<LoginViewProps, LoginViewState> {
  static contextType = userContext;
  declare context: React.ContextType<typeof userContext>;

  state = {
    fields: {
      email: '',
      password: '',
    },
    errors: {
      email: null,
      password: null,
      non_field_errors: null,
    },
    redirect: false,
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
    try {
      await this.context.login(this.state.fields);
      this.setState({ redirect: true });
    } catch (error) {
      this.setState({ errors: { ...this.state.errors, ...formErrors(error) } });
    }
  };

  render() {
    const { errors, fields, redirect } = this.state;
    if (redirect) {
      const { location } = this.props;
      const state = location.state as LocationState;
      const from = state?.from?.pathname || '/';
      return <Navigate to={from} />;
    }

    const { t } = this.props;

    return (
      <Grid container sx={{ justifyContent: 'center' }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardHeader
              title={t('login')}
              slotProps={{ title: { align: 'center' } }}
            />
            <CardContent>
              <LoginForm
                fields={fields}
                errors={errors}
                onChange={this.handleChange}
                onSubmit={this.handleSubmit}
              />
              <Grid container>
                <Grid size={{ xs: 'grow' }}>
                  <Link
                    component={RouterLink}
                    to="/password-reset/request"
                    variant="body2"
                  >
                    {t('forgot_password')}
                  </Link>
                </Grid>
                <Grid>
                  <Link component={RouterLink} to="/register" variant="body2">
                    {t('new_registration')}
                  </Link>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }
}

const RoutedView = withTranslation()(LoginView);
export default function RouteView() {
  const location = useLocation();
  return <RoutedView location={location} />;
}
