import { isAxiosError } from 'axios';

export function formErrors(error: unknown): Record<string, string[]> {
  if (
    isAxiosError<unknown>(error) &&
    typeof error.response?.data === 'object' &&
    error.response.data !== null
  ) {
    const result: Record<string, string[]> = {};
    for (const [field, messages] of Object.entries(error.response.data)) {
      if (typeof messages === 'string') {
        result[field === 'detail' ? 'non_field_errors' : field] = [messages];
      } else if (
        Array.isArray(messages) &&
        messages.every(
          (message): message is string => typeof message === 'string',
        )
      ) {
        result[field] = messages;
      }
    }
    if (Object.keys(result).length) {
      return result;
    }
  }
  return { non_field_errors: ['Request failed. Please try again.'] };
}

export function requestError(error: unknown): string {
  if (isAxiosError(error)) {
    if (error.response?.status === 401)
      return 'Your session has expired. Please log in again.';
    if (error.response?.status === 403)
      return 'You do not have permission to perform this action.';
    if (error.response?.status === 404)
      return 'The requested content is no longer available.';
  }
  return 'Request failed. Please try again.';
}
