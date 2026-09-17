import React, { useState } from 'react';
import _ from 'lodash';

import { makeStyles } from 'tss-react/mui';
import { Star } from '@mui/icons-material';

interface RatingProps {
  max: number;
  value: number;
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  onChange?: (value: number) => void;
}

const useStyles = makeStyles()({
  filledStar: {
    cursor: 'pointer',
    color: '#ffb400',
  },
  emptyStar: {
    cursor: 'pointer',
    color: '#bebebe',
  },
});

const Rating: React.FC<RatingProps> = ({
  max,
  value,
  size = 'medium',
  disabled = false,
  onChange,
}: RatingProps) => {
  const { classes } = useStyles();

  const [displayValue, setDisplayValue] = useState<number | null>(null);

  const handleMouseOver = (newValue: number): void => {
    if (!disabled) setDisplayValue(newValue + 1);
  };
  const handleMouseLeave = (): void => {
    if (!disabled) setDisplayValue(null);
  };
  const handleClick = (clickedValue: number): void => {
    if (!disabled && onChange) onChange(clickedValue + 1);
  };

  return (
    <>
      {_.range(max).map((i) => (
        <Star
          key={i}
          fontSize={size}
          className={
            i < (displayValue || value) ? classes.filledStar : classes.emptyStar
          }
          onMouseOver={() => handleMouseOver(i)}
          onFocus={() => handleMouseOver(i)}
          onMouseLeave={() => handleMouseLeave()}
          onBlur={() => handleMouseLeave()}
          onClick={() => handleClick(i)}
        />
      ))}
    </>
  );
};

export default Rating;
