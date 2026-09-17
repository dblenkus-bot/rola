import { useCallback, useEffect } from 'react';

const useKeyPress = (handler: (pressedKey: string) => void): void => {
  const downHandler = useCallback(
    ({ key }: KeyboardEvent): void => {
      handler(key);
    },
    [handler],
  );

  useEffect(() => {
    window.addEventListener('keydown', downHandler);

    return (): void => {
      window.removeEventListener('keydown', downHandler);
    };
  }, [downHandler]);
};

export default useKeyPress;
