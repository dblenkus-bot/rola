export type SeverityLevels = 'error' | 'info' | 'success' | 'warning';

export interface Notification {
  id: number;
  message: string;
  severity: SeverityLevels;
}

export type NotificationsState = Array<Notification>;

export const ADD_NOTIFICATION = 'ADD_NOTIFICATION';
export const DELETE_NOTIFICATION = 'DELETE_NOTIFICATION';

type AddNotificationAction = {
  type: typeof ADD_NOTIFICATION;
  payload: {
    message: string;
    severity: SeverityLevels;
  };
};

type DeleteNotificationAction = {
  type: typeof DELETE_NOTIFICATION;
  meta: {
    notificationId: number;
  };
};

export type NotificationsActionTypes =
  AddNotificationAction | DeleteNotificationAction;
