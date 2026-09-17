import type { DateChange } from '../../types/models';
import { DateTime } from 'luxon';
import { DatePicker as MuiDatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterLuxon } from '@mui/x-date-pickers/AdapterLuxon';

interface DatePickerProps {
  name: string;
  label: string;
  value: Date | null;
  error: string | null;
  required?: boolean;
  autoComplete: string;
  autoFocus?: boolean;
  onChange: (event: DateChange) => void;
}
export default function DatePicker({
  name,
  label,
  value,
  error,
  required = false,
  autoComplete,
  autoFocus = false,
  onChange,
}: DatePickerProps) {
  return (
    <LocalizationProvider dateAdapter={AdapterLuxon}>
      <MuiDatePicker
        name={name}
        label={label}
        value={value ? DateTime.fromJSDate(value) : null}
        openTo="year"
        views={['year', 'month', 'day']}
        format="dd. MM. yyyy"
        autoFocus={autoFocus}
        onChange={(date) => {
          if (date?.isValid) {
            onChange({ name, value: date.toJSDate() });
          }
        }}
        slotProps={{
          textField: {
            fullWidth: true,
            margin: 'normal',
            required,
            slotProps: { htmlInput: { autoComplete } },
            error: error !== null,
            helperText: error || '',
          },
        }}
      />
    </LocalizationProvider>
  );
}
