import { useCallback, useState } from "react";

import { ApiError } from "../api";

export function useAsyncAction() {
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(
    async (
      action: () => Promise<void>,
      options?: { fallbackMessage?: string; onError?: () => void },
    ): Promise<void> => {
      setError(null);
      setPending(true);
      try {
        await action();
      } catch (err) {
        setError(
          err instanceof ApiError
            ? err.message
            : (options?.fallbackMessage ?? "Что-то пошло не так"),
        );
        options?.onError?.();
      } finally {
        setPending(false);
      }
    },
    [],
  );

  return { pending, error, setError, run };
}
