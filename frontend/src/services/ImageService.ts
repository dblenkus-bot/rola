import { AxiosPromise } from 'axios';

import { apiClient } from './Base';
import { Image } from '../types/api';

export default {
  uploadImage(image: File): AxiosPromise<Image> {
    const filename = image.name.replace(/[^\x20-\x7E]|["\\]/g, ' ');
    return apiClient.post('/file', image, {
      headers: {
        'Content-Type': image.type,
        'Content-Disposition': `attachment; filename="${filename}"`,
      },
    });
  },
};
