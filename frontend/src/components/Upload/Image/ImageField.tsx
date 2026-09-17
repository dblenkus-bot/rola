import React from 'react';

import { FormControl, FormHelperText } from '@mui/material';

import ShowImage from './ShowImage';
import ImageButtons from './ImageButtons';
import ImageInput from './ImageInput';

import { ImageModel } from '../../../types/models';

export interface ImageFieldProps {
  image: ImageModel;
  handleImageChange: (payload: { file: File | undefined }) => void;
}

class ImageField extends React.Component<ImageFieldProps> {
  imageRef = React.createRef<HTMLInputElement>();

  handleClick = (): void => {
    if (this.imageRef.current) this.imageRef.current.click();
  };

  _updateImage = (file: File | undefined): void => {
    const { handleImageChange } = this.props;
    handleImageChange({ file });
  };

  handleChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    event.preventDefault();
    if (event.target.files && event.target.files.length > 0) {
      const file = event.target.files[0];
      this._updateImage(file);
    }
  };

  handleRemove = (): void => {
    this._updateImage(undefined);
  };

  render(): React.ReactNode {
    const { image } = this.props;

    const hasError = !!image.errors.file;

    return (
      <FormControl error={hasError}>
        <ImageInput handleChange={this.handleChange} imageRef={this.imageRef} />
        <ShowImage src={image.url} error={hasError} />
        <ImageButtons
          handleChange={this.handleClick}
          handleRemove={this.handleRemove}
          imageSelected={!!image.file}
        />
        {hasError && <FormHelperText>{image.errors.file}</FormHelperText>}
      </FormControl>
    );
  }
}

export default ImageField;
