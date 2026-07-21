import { makeAutoObservable, runInAction } from "mobx";

import { usersApi, type UserRead } from "../../api";
import { runAsync } from "../../shared/runAsync";

export class CoachStore {
  coachId: number | null = null;
  trainees: UserRead[] = [];
  error: string | null = null;
  pendingId: number | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  async load(coachId: number): Promise<void> {
    await runAsync(
      this,
      async () => {
        const trainees = await usersApi.getAllByCoach(coachId);
        runInAction(() => {
          this.trainees = trainees;
        });
      },
      {
        before: () => {
          this.coachId = coachId;
        },
        fallbackMessage: "Не удалось загрузить",
      },
    );
  }

  async detach(traineeId: number): Promise<void> {
    await runAsync(
      this,
      async () => {
        await usersApi.deleteCoach(traineeId);
        if (this.coachId !== null) await this.load(this.coachId);
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
