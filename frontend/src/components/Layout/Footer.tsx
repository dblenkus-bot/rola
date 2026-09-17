import React from 'react';

import { makeStyles } from 'tss-react/mui';

import Copyright from './Copyright';

const useStyles = makeStyles()((theme) => ({
  footer: {
    padding: theme.spacing(3, 2),
    marginTop: 'auto',
    backgroundColor:
      theme.palette.mode === 'light'
        ? theme.palette.grey[200]
        : theme.palette.grey[800],
  },
}));

const Footer: React.FC = () => {
  const { classes } = useStyles();

  return (
    <footer className={classes.footer}>
      <Copyright />
    </footer>
  );
};

export default Footer;
