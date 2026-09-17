import React, { ReactNode } from 'react';

import { Grid } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { uploadFormStyles } from '../../../styles/general';

interface ImageGridProps {
  children: ReactNode;
}

const useStyles = makeStyles()(uploadFormStyles);

const ImageGrid: React.FC<ImageGridProps> = (props) => {
  const { classes } = useStyles();
  const { children } = props;

  return (
    <Grid className={classes.imageGrid} size={{ xs: 12, sm: 6, md: 4 }}>
      {children}
    </Grid>
  );
};

export default ImageGrid;
