import React from 'react';
import DOMPurify from 'dompurify';

interface NoticeHtmlProps {
  notice: string;
}

const NoticeHtml: React.FC<NoticeHtmlProps> = ({ notice }) => {
  return (
    <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(notice) }} />
  );
};

export default NoticeHtml;
