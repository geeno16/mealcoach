import { makeAutoObservable, runInAction } from "mobx";

import { notificationsApi, usersApi, type NotificationRead } from "../../api";
import { runAsync } from "../../shared/runAsync";

export class NotificationStore {
  items: NotificationRead[] = [];
  error: string | null = null;
  pendingId: number | null = null;
  loading = false;

  constructor() {
    makeAutoObservable(this);
  }

  async load(): Promise<void> {
    await runAsync(this, () => this.fetch(), {
      before: () => {
        this.loading = true;
      },
      after: () => {
        this.loading = false;
      },
      fallbackMessage: "Не удалось загрузить",
    });
  }

  async accept(traineeId: number): Promise<void> {
    await this.run(traineeId, () => usersApi.approveRequest(traineeId));
  }

  async reject(traineeId: number): Promise<void> {
    await this.run(traineeId, () => usersApi.deleteCoach(traineeId));
  }

  private async fetch(): Promise<void> {
    const items = await notificationsApi.getNotifications();
    runInAction(() => {
      this.items = items;
    });
  }

  private async run(
    traineeId: number,
    action: () => Promise<unknown>,
  ): Promise<void> {
    await runAsync(
      this,
      async () => {
        await action();
        await this.fetch();
      },
      {
        before: () => {
          this.pendingId = traineeId;
        },
        after: () => {
          this.pendingId = null;
        },
      },
    );
  }
}
