import { beforeEach, describe, expect, it, vi } from 'vitest';
import store from '..';
import { contest } from '../../test/fixtures';
import {
  imageStore,
  submissionUpdate,
  uploadInit,
  uploadSetContest,
  uploadSubmit,
} from './actions';
import { getEmptyContest } from './utils';
import upload from '../../utils/upload';
import validate from '../../utils/validate';

vi.mock('../../utils/upload', () => ({ default: vi.fn() }));
vi.mock('../../utils/validate', () => ({ default: vi.fn() }));
beforeEach(() => {
  vi.clearAllMocks();
  store.dispatch(uploadInit(contest));
});
describe('submission upload state', () => {
  it('accepts browser File metadata while editing and submitting a photograph', async () => {
    const file = new File(['jpeg content'], 'photograph.jpg', {
      type: 'image/jpeg',
      lastModified: 1234,
    });
    Object.defineProperty(file, 'lastModifiedDate', {
      enumerable: true,
      get: () => new Date(file.lastModified),
    });
    store.dispatch(
      imageStore(2, 0, 0, { file, url: 'data:image/jpeg;base64,preview' }),
    );
    store.dispatch(
      submissionUpdate(2, 0, { name: 'title', value: 'Autumn trees' }),
    );
    vi.mocked(validate).mockImplementation(async (form) => form);
    vi.mocked(upload).mockResolvedValue();
    await store.dispatch(uploadSubmit());
    const submission =
      store.getState().upload.contest.themes[0]?.submissions[0];
    expect(submission?.title).toBe('Autumn trees');
    expect(submission?.images[0]?.file).toBe(file);
    expect(upload).toHaveBeenCalledWith(store.getState().upload.contest);
    expect(store.getState().upload.redirect).toBe(true);
    expect(store.getState().upload.uploading).toBe(false);
  });

  it('releases the upload button after a failed request without redirecting', async () => {
    vi.mocked(validate).mockResolvedValue(getEmptyContest());
    vi.mocked(upload).mockRejectedValue(new Error('Network failure'));
    await store.dispatch(uploadSubmit());
    expect(store.getState().upload.uploading).toBe(false);
    expect(store.getState().upload.redirect).toBe(false);
    expect(store.getState().notifications.at(-1)?.message).toBe(
      'Upload failed. Please try again.',
    );
  });
  it('clears the previous author and completion state when opening another contest', async () => {
    const form = getEmptyContest();
    form.author.first_name = 'Previous author';
    store.dispatch(uploadSetContest(form));
    vi.mocked(validate).mockResolvedValue(form);
    vi.mocked(upload).mockResolvedValue();
    await store.dispatch(uploadSubmit());
    expect(store.getState().upload.redirect).toBe(true);
    store.dispatch(uploadInit({ ...contest, id: 3 }));
    expect(store.getState().upload.redirect).toBe(false);
    expect(store.getState().upload.contest.author.first_name).toBe('');
  });
});
