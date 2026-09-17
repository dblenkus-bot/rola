import { Theme } from '@mui/material/styles';

export const uploadFormStyles = ({ spacing }: Theme) => ({
  fileInput: {
    display: 'none',
  },
  image: {
    border: '1px solid #ddd',
    borderRadius: '4px',
    maxHeight: '100%',
    padding: '5px',
    width: '100%',
  },
  button: {
    margin: spacing(1, 0, 0),
    padding: spacing(1),
  },
  submitButton: {
    padding: spacing(2),
  },
  themeCard: {
    margin: spacing(4, 0),
  },
  seriesClearfix: {
    paddingTop: '0 !important',
    paddingBottom: '0 !important',
  },
  seriesMetaGrid: {
    padding: `${spacing(0, 1)} !important`,
  },
  seriesMetaInput: {
    margin: spacing(1, 0),
  },
  imageGrid: {
    padding: `${spacing(2, 1, 0)} !important`,
  },
  error: {
    border: '1px solid #f00',
  },
  errorAlert: {
    margin: spacing(0, 0, 2),
  },
});

export const authStyles = ({ spacing }: Theme) => ({
  alert: {
    margin: spacing(2, 0, 0),
  },
  paragraph: {
    marginTop: spacing(2),
  },
  submit: {
    margin: spacing(2, 0, 2),
    padding: spacing(1),
  },
});

export const editListStyles = ({ spacing }: Theme) => ({
  button: {
    padding: spacing(0),
  },
});
