import { lazy, Suspense } from 'react';
import LoadingProgress from './components/LoadingProgress';

import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { Provider } from 'react-redux';

import { CssBaseline, Container } from '@mui/material';

import Header from './components/Layout/Header';
import Footer from './components/Layout/Footer';
import { makeStyles } from 'tss-react/mui';

const ContestsListView = lazy(() => import('./views/ContestsList'));
const ContestDetailsView = lazy(() => import('./views/ContestDetails'));
const LoginView = lazy(() => import('./views/Login'));
const RegisterView = lazy(() => import('./views/Register'));
const RegisterActivateView = lazy(() => import('./views/RegisterActivate'));
const ResultsListView = lazy(() => import('./views/ResultsList'));
const UploadView = lazy(() => import('./views/Upload'));
const UploadConfirmView = lazy(() => import('./views/UploadConfirm'));
const EditSubmissionsList = lazy(() => import('./views/EditSubmissionsList'));
const PasswordResetRequestView = lazy(
  () => import('./views/PasswordResetRequest'),
);
const PasswordResetView = lazy(() => import('./views/PasswordReset'));
const SelectThemeView = lazy(() => import('./views/judge/SelectTheme'));
const ViewThemeView = lazy(() => import('./views/judge/ViewTheme'));
const RateSubmissionView = lazy(() => import('./views/judge/RateSubmission'));
const AdminSubmissionSetList = lazy(
  () => import('./views/admin/SubmissionSetList'),
);
const AdminSubmissionSetView = lazy(
  () => import('./views/admin/SubmissionSetView'),
);

import AuthProvider from './components/Auth/AuthProvider';
import Notifications from './components/Notifications/Notifications';
import PrivateRoute from './components/Auth/PrivateRoute';

import store from './store';
const ThemeOverview = lazy(() => import('./views/judge/ThemeOverview'));
const ThemeResultsView = lazy(() => import('./views/results/ThemeResults'));
const SelectResultsThemeView = lazy(
  () => import('./views/results/SelectTheme'),
);
const SubmissionResultsView = lazy(
  () => import('./views/results/SubmissionResults'),
);

const useStyles = makeStyles()((theme) => ({
  container: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(4),
  },
  root: {
    display: 'flex',
    flexDirection: 'column',
    minHeight: '100vh',
  },
}));

const App = () => {
  const { classes } = useStyles();

  return (
    <div className={classes.root}>
      <Provider store={store}>
        <AuthProvider>
          <BrowserRouter>
            <CssBaseline />
            <Notifications />
            <Header />
            <Container className={classes.container}>
              <Suspense fallback={<LoadingProgress />}>
                <Routes>
                  <Route
                    path="/"
                    element={<Navigate to="/contests" replace />}
                  />
                  <Route path="/contests" element={<ContestsListView />} />
                  <Route
                    path="/contest/:contestId/details"
                    element={<ContestDetailsView />}
                  />
                  <Route
                    path="/contest/:contestId/upload"
                    element={
                      <PrivateRoute>
                        <UploadView />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/contest/:contestId/confirm"
                    element={
                      <PrivateRoute>
                        <UploadConfirmView />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/user/submissions"
                    element={
                      <PrivateRoute>
                        <EditSubmissionsList />
                      </PrivateRoute>
                    }
                  />
                  <Route path="/login" element={<LoginView />} />
                  <Route
                    path="/password-reset"
                    element={<PasswordResetView />}
                  />
                  <Route
                    path="/password-reset/request"
                    element={<PasswordResetRequestView />}
                  />
                  <Route path="/register" element={<RegisterView />} />
                  <Route
                    path="/register/activate"
                    element={<RegisterActivateView />}
                  />
                  <Route path="/results" element={<ResultsListView />} />

                  <Route
                    path="/results/contest/:contestId/theme/:themeId/submission/:submissionId"
                    element={<SubmissionResultsView />}
                  />
                  <Route
                    path="/results/contest/:contestId/theme/:themeId"
                    element={<ThemeResultsView />}
                  />
                  <Route
                    path="/results/contest/:contestId"
                    element={<SelectResultsThemeView />}
                  />

                  <Route
                    path="/judge"
                    element={
                      <PrivateRoute>
                        <SelectThemeView />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/judge/contest/:contestId/theme/:themeId"
                    element={
                      <PrivateRoute>
                        <ViewThemeView />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/judge/contest/:contestId/theme/:themeId/rate"
                    element={
                      <PrivateRoute>
                        <RateSubmissionView />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/judge/contest/:contestId/theme/:themeId/overview"
                    element={
                      <PrivateRoute>
                        <ThemeOverview />
                      </PrivateRoute>
                    }
                  />

                  <Route
                    path="/admin/contest/:contestId/submissions"
                    element={
                      <PrivateRoute>
                        <AdminSubmissionSetList />
                      </PrivateRoute>
                    }
                  />
                  <Route
                    path="/admin/contest/:contestId/submission/:submissionSetId"
                    element={
                      <PrivateRoute>
                        <AdminSubmissionSetView />
                      </PrivateRoute>
                    }
                  />
                </Routes>
              </Suspense>
            </Container>
            <Footer />
          </BrowserRouter>
        </AuthProvider>
      </Provider>
    </div>
  );
};

export default App;
