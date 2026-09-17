import type { InputChange } from '../types/models';
import React from 'react';

import { withTranslation, WithTranslation } from 'react-i18next';

import { Alert, Card, CardContent, CardHeader, Grid } from '@mui/material';

import PasswordResetRequestForm, {
  Fields,
} from '../components/Auth/PasswordResetRequestForm';
import PasswordResetRequestConfirm from '../components/Auth/PasswordResetRequestConfirm';

import UserService from '../services/UserService';

type PasswordResetRequestViewProps = WithTranslation;

interface PasswordResetRequestViewState {
  error: boolean;
  done: boolean;
  fields: Fields;
}

class PasswordResetRequestView extends React.Component<
  PasswordResetRequestViewProps,
  PasswordResetRequestViewState
> {
  state = {
    error: false,
    done: false,
    fields: {
      email: '',
    },
  };

  handleChange = ({ name, value }: InputChange): void => {
    this.setState((state) => {
      const fields: Fields = Object.assign({}, state.fields);
      fields[name] = value;
      return { fields };
    });
  };

  handleSubmit = async (): Promise<void> => {
    const { fields } = this.state;
    try {
      await UserService.requestPasswordReset(fields);
      this.setState({ done: true });
    } catch {
      this.setState({ error: true });
    }
  };

  render() {
    const { done, fields } = this.state;
    const { t } = this.props;

    return (
      <Grid container sx={{ justifyContent: 'center' }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardHeader
              title={t('password_reset')}
              slotProps={{ title: { align: 'center' } }}
            />
            <CardContent>
              {this.state.error && (
                <Alert severity="error">
                  Request failed. Please try again.
                </Alert>
              )}
              {done ? (
                <PasswordResetRequestConfirm email={fields.email} />
              ) : (
                <PasswordResetRequestForm
                  fields={fields}
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

export default withTranslation()(PasswordResetRequestView);
