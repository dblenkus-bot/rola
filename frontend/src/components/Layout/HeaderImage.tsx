import React from 'react';

import { makeStyles } from 'tss-react/mui';

interface HeaderImageProps {
  src: string;
}

const useStyles = makeStyles()({
  image: {
    maxWidth: '100%',
  },
});

const HeaderImage: React.FC<HeaderImageProps> = ({ src }) => {
  const { classes } = useStyles();

  return <img src={src} alt="Header" className={classes.image} />;
};

export default HeaderImage;
