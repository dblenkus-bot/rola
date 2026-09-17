import english from './locales/en/translations.json';
import slovenian from './locales/sl/translations.json';
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    supportedLngs: ['en', 'sl'],
    interpolation: { escapeValue: false },
    resources: {
      en: {
        translations: english,
      },
      sl: {
        translations: slovenian,
      },
    },
    ns: ['translations'],
    defaultNS: 'translations',
    detection: {
      lookupQuerystring: 'lang',
      lookupCookie: 'lang',
      lookupLocalStorage: 'lang',
    },
  });

export default i18n;
