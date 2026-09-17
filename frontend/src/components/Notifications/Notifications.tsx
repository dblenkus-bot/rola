import { useDispatch, useSelector } from 'react-redux';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import type { AppDispatch, AppState } from '../../store';
import { deleteMessage } from '../../store/notifications/actions';

export default function Notifications() {
  const dispatch = useDispatch<AppDispatch>();
  const notification = useSelector((state: AppState) =>
    state.notifications.at(-1),
  );
  if (!notification) {
    return null;
  }
  const close = () => {
    dispatch(deleteMessage(notification.id));
  };
  return (
    <Snackbar
      key={notification.id}
      open
      autoHideDuration={6000}
      onClose={(_, reason) => {
        if (reason !== 'clickaway') {
          close();
        }
      }}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert severity={notification.severity} variant="filled" onClose={close}>
        {notification.message}
      </Alert>
    </Snackbar>
  );
}
