import React from 'react';

import CircularProgress from '@mui/material/CircularProgress';

const LoadingProgress: React.FC = () => (
  <div style={{ display: 'flex', justifyContent: 'center' }}>
    <CircularProgress />
  </div>
);

export default LoadingProgress;
