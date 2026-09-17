import type { InputChange } from '../../types/models';
import React from 'react';

import { TextField } from '@mui/material';

export interface InputFieldProps {
  className: string;
  name: string;
  label: string;
  value: string;
  error: string | null;
  autoComplete: string;
  type: string;
  required: boolean;
  rows: number;
  autoFocus: boolean;
  onChange: (event: InputChange) => void;
}

class InputField extends React.Component<InputFieldProps> {
  static defaultProps = {
    className: '',
    type: 'text',
    value: '',
    error: null,
    required: false,
    rows: 1,
    autoFocus: false,
  };

  onChange = ({ target }: React.ChangeEvent<HTMLInputElement>): void => {
    const { value } = target;
    const { onChange, name } = this.props;
    onChange({ name, value });
  };

  render(): React.ReactNode {
    const {
      autoComplete,
      autoFocus,
      className,
      label,
      name,
      required,
      rows,
      type,
      value,
      error,
    } = this.props;

    return (
      <TextField
        className={className}
        name={name}
        variant="outlined"
        margin="normal"
        fullWidth
        label={label}
        type={type}
        required={required}
        multiline={rows > 1}
        rows={rows}
        autoComplete={autoComplete}
        autoFocus={autoFocus}
        onChange={this.onChange}
        value={value}
        error={error !== null}
        helperText={error || ''}
      />
    );
  }
}

export default InputField;
