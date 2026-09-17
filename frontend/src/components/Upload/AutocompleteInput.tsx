import React, { ReactNode } from 'react';

import Autocomplete from '@mui/material/Autocomplete';
import { CircularProgress, TextField } from '@mui/material';

import { InputChange } from '../../types/models';
import { Institution } from '../../types/api';
import InstitutionService from '../../services/InstitutionService';

export interface AutocompleteFieldProps {
  name: string;
  label: string;
  value: string;
  error: string | null;
  required: boolean;
  autoFocus?: boolean;
  onChange: (event: InputChange) => void;
}

const AutocompleteField: React.FC<AutocompleteFieldProps> = ({
  name,
  label,
  value,
  required,
  error,
  autoFocus,
  onChange,
}: AutocompleteFieldProps) => {
  const [open, setOpen] = React.useState(false);
  const [options, setOptions] = React.useState<Institution[]>([]);
  const [loading, setLoading] = React.useState(false);
  const [failed, setFailed] = React.useState(false);

  const handleChange = (
    event: React.SyntheticEvent,
    institution: Institution | null,
  ): void => {
    onChange({ name, value: institution ? institution.name : '' });
  };

  React.useEffect(() => {
    if (!open) {
      return;
    }
    let active = true;
    setLoading(true);
    setFailed(false);
    InstitutionService.getInstitutions()
      .then(({ data }) => {
        if (active) {
          setOptions(data.results);
        }
      })
      .catch(() => {
        if (active) {
          setFailed(true);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });
    return () => {
      active = false;
    };
  }, [open]);

  return (
    <Autocomplete<Institution>
      value={options.find((institution) => institution.name === value) ?? null}
      open={open}
      onOpen={(): void => {
        setOpen(true);
      }}
      onClose={(): void => {
        setOpen(false);
      }}
      isOptionEqualToValue={(option, selected): boolean =>
        option.name === selected.name
      }
      getOptionLabel={(option): string => option.name}
      options={options}
      loading={loading}
      onChange={handleChange}
      renderInput={(params): ReactNode => (
        <TextField
          {...params}
          name={name}
          variant="outlined"
          margin="normal"
          fullWidth
          label={label}
          required={required}
          autoFocus={autoFocus}
          error={error !== null || failed}
          helperText={error || (failed ? 'Could not load institutions.' : '')}
          slotProps={{
            ...params.slotProps,
            input: {
              ...params.slotProps.input,
              endAdornment: (
                <>
                  {loading && <CircularProgress color="inherit" size={20} />}
                  {params.slotProps.input.endAdornment}
                </>
              ),
            },
          }}
        />
      )}
    />
  );
};

export default AutocompleteField;
