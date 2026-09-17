import { useLocation, type Location } from 'react-router-dom';
import React from 'react';

import { WithTranslation, withTranslation } from 'react-i18next';

import { isString } from 'lodash';

import { Navigate } from 'react-router-dom';

import { Card, CardContent, CardHeader, Grid } from '@mui/material';

import RegisterActivateFailed from '../components/Auth/RegisterActivateFailed';
import RegisterActivateSuccess from '../components/Auth/RegisterActivateSuccess';

import UserService from '../services/UserService';

interface RegisterActivateViewProps extends WithTranslation {
  location: Location;
}

interface RegisterActivateViewState {
  succeeded: boolean | null;
  redirect: boolean;
}

class RegisterActivateView extends React.Component<
  RegisterActivateViewProps,
  RegisterActivateViewState
> {
  state = {
    succeeded: null,
    redirect: false,
  };

  async componentDidMount() {
    const { location } = this.props;
    const token = new URLSearchParams(location.search).get('token') || '';
    if (isString(token)) {
      try {
        await UserService.activateUser({ token });
        this.setState({ succeeded: true });
      } catch {
        this.setState({ succeeded: false });
      }
    } else {
      this.setState({ succeeded: false });
    }
  }

  handleClick = () => this.setState({ redirect: true });

  render() {
    const { redirect, succeeded } = this.state;
    const { t } = this.props;

    if (redirect) {
      return <Navigate to="/login" />;
    }

    if (succeeded === null) {
      return <></>;
    }

    return (
      <Grid container sx={{ justifyContent: 'center' }}>
        <Grid size={{ xs: 12, sm: 6, md: 4 }}>
          <Card>
            <CardHeader
              title={t('account_activation')}
              slotProps={{ title: { align: 'center' } }}
            />
            <CardContent>
              {succeeded ? (
                <RegisterActivateSuccess onClick={this.handleClick} />
              ) : (
                <RegisterActivateFailed />
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    );
  }
}

const RoutedView = withTranslation()(RegisterActivateView);
export default function RouteView() {
  const location = useLocation();
  return <RoutedView location={location} />;
}
