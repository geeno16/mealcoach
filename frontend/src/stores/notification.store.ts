import { makeAutoObservable, runInAction } from "mobx";

import {
  ApiError,
  notificationsApi,
  usersApi,
  type NotificationRead,
} from "../api";

export class NotificationStore {
  items: NotificationRead[] = [];
  error: string | null = null;
  pendingId: number | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  async load(): Promise<void> {
    runInAction(() => {
      this.error = null;
    });
    try {
      const items = await notificationsApi.getNotifications();
      runInAction(() => {
        this.items = items;
      });
    } catch (err) {
      runInAction(() => {
        this.error =
          err instanceof ApiError ? err.message : "Не удалось загрузить";
      });
    }
  }

  async accept(traineeId: number): Promise<void> {
    await this.run(traineeId, () => usersApi.approveRequest(traineeId));
  }

  async reject(traineeId: number): Promise<void> {
    await this.run(traineeId, () => usersApi.deleteCoach(traineeId));
  }

  private async run(
    traineeId: number,
    action: () => Promise<unknown>,
  ): Promise<void> {
    runInAction(() => {
      this.error = null;
      this.pendingId = traineeId;
    });
    try {
      await action();
      await this.load();
    } catch (err) {
      runInAction(() => {
        this.error = err instanceof ApiError ? err.message : "Ошибка";
      });
    } finally {
      runInAction(() => {
        this.pendingId = null;
      });
    }
  }
}
