import {
  ADD_NOTIFICATION,
  DELETE_NOTIFICATION,
  Notification,
  NotificationsActionTypes,
  NotificationsState,
} from './types';

const initialState: NotificationsState = [];

let nextId = 1;

const reducer = (
  state = initialState,
  action: NotificationsActionTypes,
): NotificationsState => {
  switch (action.type) {
    case ADD_NOTIFICATION: {
      const newNotification = { id: nextId, ...action.payload };
      nextId += 1;
      return [...state, newNotification];
    }
    case DELETE_NOTIFICATION: {
      return state.filter(
        (notification: Notification) =>
          notification.id !== action.meta.notificationId,
      );
    }
    default: {
      return state;
    }
  }
};

export default reducer;
