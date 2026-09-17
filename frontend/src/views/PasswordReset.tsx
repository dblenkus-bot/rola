import type { InputChange } from '../types/models';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { isString } from 'lodash';

import { Redirect, RouteComponentProps, withRouter } from 'react-router-dom';
import { parse } from 'query-string';

import { Card, CardContent, CardHeader, Grid } from '@material-ui/core';

import PasswordResetForm, {
  Errors,
  Fields,
} from '../components/Auth/PasswordResetForm';
import PasswordResetSuccess from '../components/Auth/PasswordResetSuccess';

import UserService from '../services/UserService';

interface PasswordResetProps extends RouteComponentProps, WithTranslation {}

interface PasswordResetState {
  fields: Fields;
  errors: Errors;
  done: boolean;
  redirect: boolean;
}

class PasswordResetView extends React.Component<
  PasswordResetProps,
  PasswordResetState
> {
  state = {
    fields: {
      new_password: '',
    },
    errors: {
      new_password: null,
      non_field_errors: null,
    },
    done: false,
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
    const { fields } = this.state;
    const { location } = this.props;
    const token = parse(location.search)['token'] || '';
    if (isString(token)) {
      try {
        await UserService.passwordReset({ ...fields, token });
        this.setState({ done: true });
      } catch (error) {
        this.setState({ errors: error.response.data });
      }
    } else {
      const errors: Errors = Object.assign({}, this.state.errors);
      errors.non_field_errors = ['Invalid password reset token.'];
      this.setState({ errors });
    }
  };

  handleClick = () => this.setState({ redirect: true });

  render() {
    const { done, errors, fields, redirect } = this.state;
    const { t } = this.props;

    if (redirect) {
      return <Redirect to="/login" />;
    }

    return (
      <Grid container justify="center">
        <Grid item xs={12} sm={6} md={4}>
          <Card>
            <CardHeader
              title={t('password_reset')}
              titleTypographyProps={{ align: 'center' }}
            />
            <CardContent>
              {done ? (
                <PasswordResetSuccess onClick={this.handleClick} />
              ) : (
                <PasswordResetForm
                  fields={fields}
                  errors={errors}
                  onChange={this.handleChange}
                  onSubmit={this.handleSubmit}
                />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }
}

export default withTranslation()(withRouter(PasswordResetView));
