import React, { ReactNode } from 'react';

import { Grid } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { uploadFormStyles } from '../../../styles/general';

interface SeriesGridProps {
  titleField: ReactNode;
  descriptionField: ReactNode;
}

const useStyles = makeStyles()(uploadFormStyles);

const SeriesGrid: React.FC<SeriesGridProps> = (props) => {
  const { classes } = useStyles();
  const { titleField, descriptionField } = props;

  return (
    <>
      <Grid className={classes.seriesClearfix} size={{ xs: 12 }} />
      <Grid className={classes.seriesMetaGrid} size={{ xs: 12, sm: 6, md: 4 }}>
        {titleField}
      </Grid>
      <Grid className={classes.seriesMetaGrid} size={{ xs: 12 }}>
        {descriptionField}
      </Grid>
    </>
  );
};

export default SeriesGrid;
