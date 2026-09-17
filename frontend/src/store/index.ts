import {
  configureStore,
  combineReducers,
  type ThunkAction,
  type UnknownAction,
} from '@reduxjs/toolkit';
import contests from './contests/reducer';
import notifications from './notifications/reducer';
import upload from './upload/reducer';
import jury from './jury/reducer';

const rootReducer = combineReducers({ contests, notifications, upload, jury });
export type AppState = ReturnType<typeof rootReducer>;
export type AppThunk<R = void> = ThunkAction<
  R,
  AppState,
  unknown,
  UnknownAction
>;

const store = configureStore({
  reducer: rootReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['AUTHOR_UPDATE', 'IMAGE_STORE', 'UPLOAD_SET_CONTEST'],
        ignoredPaths: ['upload.contest'],
      },
    }),
});
export type AppDispatch = typeof store.dispatch;
export default store;
