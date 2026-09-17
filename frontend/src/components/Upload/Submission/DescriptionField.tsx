import React from 'react';

import { useTranslation } from 'react-i18next';

import { makeStyles } from 'tss-react/mui';

import { SubmissionModel, InputChange } from '../../../types/models';
import { uploadFormStyles } from '../../../styles/general';

import InputField from '../InputField';

export interface DescriptionFieldProps {
  submission: SubmissionModel;
  onChange: (payload: InputChange) => void;
}

const useStyles = makeStyles()(uploadFormStyles);

const DescriptionField: React.FC<DescriptionFieldProps> = (props) => {
  const { classes } = useStyles();
  const { t } = useTranslation();
  const { submission, onChange } = props;

  return (
    <InputField
      className={classes.seriesMetaInput}
      name="description"
      value={submission.description}
      error={submission.errors.description}
      label={t('description')}
      autoComplete=""
      required={submission.meta.descriptionRequired}
      rows={3}
      onChange={onChange}
    />
  );
};

export default DescriptionField;
