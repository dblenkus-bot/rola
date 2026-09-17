import React, { ReactNode } from 'react';

import { Card, CardContent, CardHeader, Grid } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import { uploadFormStyles } from '../../../styles/general';

export interface ThemeCardProps {
  title: string;
  children: ReactNode;
}

const useStyles = makeStyles()(uploadFormStyles);

const ThemeCard: React.FC<ThemeCardProps> = (props) => {
  const { classes } = useStyles();
  const { title, children } = props;

  return (
    <Card className={classes.themeCard} raised>
      <CardHeader
        title={title}
        slotProps={{
          title: { component: 'h3', align: 'center', variant: 'h3' },
        }}
      />
      <CardContent>
        <Grid container spacing={2} sx={{ alignItems: 'center' }}>
          {children}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default ThemeCard;
