import { makeAutoObservable, runInAction } from "mobx";

import { usersApi, type UserRead } from "../../api";
import { runAsync } from "../../shared/runAsync";

export class CoachStore {
  coachId: number | null = null;
  trainees: UserRead[] = [];
  error: string | null = null;
  pendingId: number | null = null;
  loading = false;

  constructor() {
    makeAutoObservable(this);
  }

  async load(coachId: number): Promise<void> {
    await runAsync(this, () => this.fetch(coachId), {
      before: () => {
        this.coachId = coachId;
        this.loading = true;
      },
      after: () => {
        this.loading = false;
      },
      fallbackMessage: "Не удалось загрузить",
    });
  }

  async detach(traineeId: number): Promise<void> {
    await runAsync(
      this,
      async () => {
        await usersApi.deleteCoach(traineeId);
        if (this.coachId !== null) await this.fetch(this.coachId);
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

  private async fetch(coachId: number): Promise<void> {
    const trainees = await usersApi.getAllByCoach(coachId);
    runInAction(() => {
      this.trainees = trainees;
    });
  }
}
