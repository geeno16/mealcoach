import { makeAutoObservable, runInAction } from "mobx";

import { ApiError, usersApi, type UserRead } from "../api";

export class CoachStore {
  coachId: number | null = null;
  requests: UserRead[] = [];
  trainees: UserRead[] = [];
  error: string | null = null;
  pendingId: number | null = null;

  constructor() {
    makeAutoObservable(this);
  }

  async load(coachId: number): Promise<void> {
    runInAction(() => {
      this.coachId = coachId;
      this.error = null;
    });
    try {
      const [requests, trainees] = await Promise.all([
        usersApi.getRequests(coachId),
        usersApi.getAllByCoach(coachId),
      ]);
      runInAction(() => {
        this.requests = requests;
        this.trainees = trainees;
      });
    } catch (err) {
      runInAction(() => {
        this.error =
          err instanceof ApiError ? err.message : "Не удалось загрузить";
      });
    }
  }

  async approve(traineeId: number): Promise<void> {
    await this.run(traineeId, () => usersApi.approveRequest(traineeId));
  }

  async detach(traineeId: number): Promise<void> {
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
      if (this.coachId !== null) await this.load(this.coachId);
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
