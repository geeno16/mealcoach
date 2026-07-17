import { makeAutoObservable, runInAction } from "mobx";

import { ApiError, postsApi, type PostRead } from "../api";

export class PostsStore {
  items: PostRead[] = [];
  error: string | null = null;
  loading = false;

  constructor() {
    makeAutoObservable(this);
  }

  async load(authId: number): Promise<void> {
    runInAction(() => {
      this.error = null;
      this.loading = true;
    });
    try {
      const items = await postsApi.getAllByAuth(authId);
      runInAction(() => {
        this.items = items;
      });
    } catch (err) {
      runInAction(() => {
        this.error =
          err instanceof ApiError ? err.message : "Не удалось загрузить";
      });
    } finally {
      runInAction(() => {
        this.loading = false;
      });
    }
  }
}
