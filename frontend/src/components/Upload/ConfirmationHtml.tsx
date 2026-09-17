import { useEffect, useRef } from 'react';

let paypalReady: Promise<void> | undefined;
function loadPaypal(): Promise<void> {
  const clientId = import.meta.env.VITE_PAYPAL_CLIENT_ID;
  if (!clientId) {
    return Promise.resolve();
  }
  paypalReady ??= new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const query = new URLSearchParams({
      'client-id': clientId,
      currency: 'EUR',
      'enable-funding': 'venmo',
    });
    script.src = `https://www.paypal.com/sdk/js?${query}`;
    script.onload = () => resolve();
    script.onerror = () => {
      paypalReady = undefined;
      script.remove();
      reject(new Error('Payment provider could not be loaded.'));
    };
    document.head.appendChild(script);
  });
  return paypalReady;
}

export default function ConfirmationHtml({ html }: { html: string }) {
  const container = useRef<HTMLDivElement>(null);
  useEffect(() => {
    let cancelled = false;
    const element = container.current;
    loadPaypal()
      .then(() => {
        if (cancelled || !container.current) {
          return;
        }
        // Only trusted administrators may edit this template; payment integrations execute scripts.
        const range = document.createRange();
        range.selectNode(container.current);
        container.current.replaceChildren(range.createContextualFragment(html));
      })
      .catch((error: unknown) => {
        if (!cancelled && container.current) {
          container.current.textContent =
            error instanceof Error
              ? error.message
              : 'Payment provider could not be loaded.';
        }
      });
    return () => {
      cancelled = true;
      element?.replaceChildren();
    };
  }, [html]);
  return <div ref={container} />;
}
