import { makeAutoObservable, runInAction } from "mobx";

import { pictureApi, postsApi, type PostRead, type PostWrite } from "../../api";
import { runAsync } from "../../shared/runAsync";

export class PostsStore {
  items: PostRead[] = [];
  error: string | null = null;
  loading = false;
  photoVersions: Record<number, number> = {};

  constructor() {
    makeAutoObservable(this);
  }

  async load(authId: number): Promise<void> {
    await runAsync(
      this,
      async () => {
        const items = await postsApi.getAllByAuth(authId);
        runInAction(() => {
          this.items = items;
        });
      },
      {
        before: () => {
          this.loading = true;
        },
        after: () => {
          this.loading = false;
        },
        fallbackMessage: "Не удалось загрузить",
      },
    );
  }

  async createPost(data: PostWrite): Promise<PostRead> {
    const created = await postsApi.createPost(data);
    runInAction(() => {
      this.items = [created, ...this.items];
    });
    return created;
  }

  async updatePost(id: number, data: PostWrite): Promise<PostRead> {
    const updated = await postsApi.updatePost(id, data);
    runInAction(() => {
      this.items = this.items.map((p) => (p.id === id ? updated : p));
    });
    return updated;
  }

  async deletePost(id: number): Promise<void> {
    await postsApi.deletePost(id);
    runInAction(() => {
      this.items = this.items.filter((p) => p.id !== id);
    });
  }

  async setMealPicture(
    postId: number,
    mealId: number,
    data: Blob,
  ): Promise<void> {
    const picture = await pictureApi.setMealPicture(mealId, data);
    runInAction(() => {
      this.photoVersions = { ...this.photoVersions, [mealId]: Date.now() };
      this.items = this.items.map((p) => {
        if (p.id !== postId) return p;
        return {
          ...p,
          meals: p.meals?.map((m) =>
            m.id === mealId ? { ...m, picture_id: picture.id } : m,
          ),
        };
      });
    });
  }

  pictureUrl = (pictureId: number, mealId: number): string => {
    const version = this.photoVersions[mealId];
    return version
      ? `/api/pictures/${pictureId}?v=${version}`
      : `/api/pictures/${pictureId}`;
  };
}
