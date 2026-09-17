import React from 'react';

import { Link } from 'react-router-dom';

import { useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { IconButton, Menu, MenuItem } from '@mui/material';
import AccountCircle from '@mui/icons-material/AccountCircle';
import { makeStyles } from 'tss-react/mui';

import { userContext } from '../Auth/AuthProvider';

const useStyles = makeStyles()({
  menuItem: {
    textDecoration: 'none',
    color: 'inherit',
  },
});

const Dropdown: React.FC = () => {
  const user = React.useContext(userContext);
  const location = useLocation();
  const { t } = useTranslation();

  const { classes } = useStyles();
  const [anchorEl, setAnchorEl] = React.useState<null | Element>(null);

  const openMenu = (event: React.MouseEvent): void => {
    setAnchorEl(event.currentTarget);
  };

  const closeMenu = (): void => {
    setAnchorEl(null);
  };

  const logOut = (): void => {
    user.logout();
    setAnchorEl(null);
  };

  const publicMenu = [
    <Link
      to="/register"
      className={classes.menuItem}
      onClick={closeMenu}
      key="link-1"
    >
      <MenuItem>{t('register')}</MenuItem>
    </Link>,
    <Link
      to="/login"
      state={{ from: location }}
      className={classes.menuItem}
      onClick={closeMenu}
      key="link-2"
    >
      <MenuItem>{t('login')}</MenuItem>
    </Link>,
  ];

  const privateMenu = [
    <MenuItem key="item-1" onClick={closeMenu}>
      {t('profile')}
    </MenuItem>,
    <MenuItem key="item-2" onClick={logOut}>
      {t('logout')}
    </MenuItem>,
  ];

  return (
    <>
      <IconButton
        aria-label="account of current user"
        aria-controls="menu-appbar"
        aria-haspopup="true"
        onClick={openMenu}
        color="inherit"
      >
        <AccountCircle />
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={closeMenu}
      >
        {user.isLoggedIn() ? privateMenu : publicMenu}
      </Menu>
    </>
  );
};

export default Dropdown;
