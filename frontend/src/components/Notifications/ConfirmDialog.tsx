import React from 'react';

import { useTranslation } from 'react-i18next';

import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';

interface ConfirmDialogProps {
  children: React.ReactNode;
  title: string;
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

const ConfirmDialog: React.FC<ConfirmDialogProps> = (props) => {
  const { title, children, open, onClose, onConfirm } = props;

  const { t } = useTranslation();

  const handleConfirm = () => {
    onClose();
    onConfirm();
  };

  return (
    <Dialog open={open} onClose={onClose}>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>{children}</DialogContent>
      <DialogActions>
        <Button variant="contained" onClick={onClose} color="secondary">
          {t('no')}
        </Button>
        <Button variant="contained" onClick={handleConfirm} color="primary">
          {t('yes')}
        </Button>
      </DialogActions>
    </Dialog>
  );
};
export default ConfirmDialog;
