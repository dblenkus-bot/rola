import React from 'react';
import { useTranslation } from 'react-i18next';

import { Link } from 'react-router-dom';

import { AppBar, Button, Toolbar, Typography } from '@mui/material';
import { makeStyles } from 'tss-react/mui';

import Dropdown from './Dropdown';

const useStyles = makeStyles()((theme) => ({
  menuButton: {
    marginRight: theme.spacing(2),
  },
  title: {
    flexGrow: 1,
  },
}));

const Header: React.FC = () => {
  const { classes } = useStyles();
  const { i18n, t } = useTranslation();

  const handleLanguageChange = (
    event: React.MouseEvent<HTMLButtonElement>,
  ): void => {
    i18n.changeLanguage(event.currentTarget.value);
  };

  return (
    <AppBar position="sticky">
      <Toolbar>
        <Typography variant="h6" className={classes.title}>
          Rolca
        </Typography>
        <Button
          to="/contests"
          component={Link}
          className={classes.menuButton}
          color="inherit"
        >
          {t('active_contests')}
        </Button>
        <Button
          to="/user/submissions"
          component={Link}
          className={classes.menuButton}
          color="inherit"
        >
          {t('edit_submissions')}
        </Button>
        <Button
          to="/results"
          component={Link}
          className={classes.menuButton}
          color="inherit"
        >
          {t('results')}
        </Button>

        {i18n.language === 'en' ? (
          <Button onClick={handleLanguageChange} value="sl" color="inherit">
            SI
          </Button>
        ) : (
          <Button onClick={handleLanguageChange} value="en" color="inherit">
            EN
          </Button>
        )}

        <Dropdown />
      </Toolbar>
    </AppBar>
  );
};

export default Header;
