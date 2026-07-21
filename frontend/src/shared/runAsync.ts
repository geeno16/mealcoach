import { runInAction } from "mobx";

import { ApiError } from "../api";

export async function runAsync(
  target: { error: string | null },
  action: () => Promise<void>,
  options?: {
    fallbackMessage?: string;
    before?: () => void;
    after?: () => void;
  },
): Promise<void> {
  runInAction(() => {
    target.error = null;
    options?.before?.();
  });
  try {
    await action();
  } catch (err) {
    runInAction(() => {
      target.error =
        err instanceof ApiError
          ? err.message
          : (options?.fallbackMessage ?? "Ошибка");
    });
  } finally {
    if (options?.after) runInAction(options.after);
  }
}
