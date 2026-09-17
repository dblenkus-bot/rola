import type { InputChange } from '../types/models';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import {
  Link as RouterLink,
  Redirect,
  RouteComponentProps,
  withRouter,
} from 'react-router-dom';

import { Card, CardContent, CardHeader, Grid, Link } from '@material-ui/core';

import { userContext } from '../components/Auth/AuthProvider';
import LoginForm, { Errors, Fields } from '../components/Auth/LoginForm';

interface LoginViewProps extends RouteComponentProps, WithTranslation {}

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
      this.setState({ errors: error.response.data });
    }
  };

  render() {
    const { errors, fields, redirect } = this.state;
    if (redirect) {
      const { location } = this.props;
      const state = location.state as LocationState;
      const from = state?.from?.pathname || '/';
      return <Redirect to={from} />;
    }

    const { t } = this.props;

    return (
      <Grid container justify="center">
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader
              title={t('login')}
              titleTypographyProps={{ align: 'center' }}
            />
            <CardContent>
              <LoginForm
                fields={fields}
                errors={errors}
                onChange={this.handleChange}
                onSubmit={this.handleSubmit}
              />
              <Grid container>
                <Grid item xs>
                  <Link
                    component={RouterLink}
                    to="/password-reset/request"
                    variant="body2"
                  >
                    {t('forgot_password')}
                  </Link>
                </Grid>
                <Grid item>
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

export default withTranslation()(withRouter(LoginView));
