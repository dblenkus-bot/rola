import React from 'react';

import { useTranslation } from 'react-i18next';

const ResultsListView: React.FC = () => {
  const { t } = useTranslation();

  return <>{t('results')}</>;
};

export default ResultsListView;
