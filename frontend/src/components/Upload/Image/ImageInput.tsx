import React from 'react';

import { makeStyles } from 'tss-react/mui';

import { uploadFormStyles } from '../../../styles/general';

export interface ImageButtonsProps {
  handleChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  imageRef: React.RefObject<HTMLInputElement | null>;
}

const useStyles = makeStyles()(uploadFormStyles);

const ImageButtons: React.FC<ImageButtonsProps> = (props) => {
  const { classes } = useStyles();
  const { handleChange, imageRef } = props;

  return (
    <input
      className={classes.fileInput}
      type="file"
      accept="image/jpeg"
      aria-label="Select photograph"
      onChange={handleChange}
      ref={imageRef}
    />
  );
};

export default ImageButtons;
