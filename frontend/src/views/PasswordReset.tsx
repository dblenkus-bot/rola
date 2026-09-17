import type { InputChange } from '../types/models';
import { formErrors } from '../services/errors';
import { useLocation, type Location } from 'react-router-dom';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { Navigate } from 'react-router-dom';

import { Card, CardContent, CardHeader, Grid } from '@mui/material';

import PasswordResetForm, {
  Errors,
  Fields,
} from '../components/Auth/PasswordResetForm';
import PasswordResetSuccess from '../components/Auth/PasswordResetSuccess';

import UserService from '../services/UserService';

interface PasswordResetProps extends WithTranslation {
  location: Location;
}

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
    const token = new URLSearchParams(location.search).get('token') || '';
    if (token) {
      try {
        await UserService.passwordReset({ ...fields, token });
        this.setState({ done: true });
      } catch (error) {
        this.setState({
          errors: { ...this.state.errors, ...formErrors(error) },
        });
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
      return <Navigate to="/login" />;
    }

    return (
      <Grid container sx={{ justifyContent: 'center' }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardHeader
              title={t('password_reset')}
              slotProps={{ title: { align: 'center' } }}
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

const RoutedView = withTranslation()(PasswordResetView);
export default function RouteView() {
  const location = useLocation();
  return <RoutedView location={location} />;
}
