import { makeAutoObservable, runInAction } from "mobx";

import {
  type MealRead,
  type MealWrite,
  type PostRead,
  type PostWrite,
} from "../../api";
import { runAsync } from "../../shared/runAsync";
import {
  MAX_POST_MEALS,
  MIN_POST_MEALS,
  validateMealMacro,
  validateMealName,
  validatePostDescription,
  validatePostName,
} from "../../shared/validation";
import { type SessionStore } from "../auth/session.store";

import { type PostsStore } from "./posts.store";

export type MealDraft = {
  id: number;
  name: string;
  cal: string;
  protein: string;
  fat: string;
  carbohydrate: string;
};

export type MealDraftErrors = {
  name: string | null;
  cal: string | null;
  protein: string | null;
  fat: string | null;
  carbohydrate: string | null;
};

function emptyDraft(id: number): MealDraft {
  return { id, name: "", cal: "", protein: "", fat: "", carbohydrate: "" };
}

function toDraft(meal: MealRead): MealDraft {
  return {
    id: meal.id,
    name: meal.name ?? "",
    cal: meal.cal?.toString() ?? "",
    protein: meal.protein?.toString() ?? "",
    fat: meal.fat?.toString() ?? "",
    carbohydrate: meal.carbohydrate?.toString() ?? "",
  };
}

function toNumber(value: string): number | null {
  return value === "" ? null : Number(value);
}

function toMealWrite(draft: MealDraft): MealWrite {
  return {
    id: draft.id > 0 ? draft.id : null,
    name: draft.name || null,
    cal: toNumber(draft.cal),
    protein: toNumber(draft.protein),
    fat: toNumber(draft.fat),
    carbohydrate: toNumber(draft.carbohydrate),
  };
}

function revokePreviews(previews: Record<number, string>): void {
  Object.values(previews).forEach((url) => URL.revokeObjectURL(url));
}

export class PostDraftStore {
  readonly postId: number | null;
  readonly isCreate: boolean;

  editing: boolean;
  name: string;
  description: string;
  mealDrafts: MealDraft[] = [];
  photoFiles: Record<number, File> = {};
  photoPreviews: Record<number, string> = {};
  pending = false;
  error: string | null = null;
  confirmingDelete = false;
  confirmingClose = false;
  confirmingCancelEdit = false;
  submitted = false;

  private nextDraftId = -1;
  private readonly posts: PostsStore;
  private readonly session: SessionStore;

  constructor(posts: PostsStore, session: SessionStore, post: PostRead | null) {
    this.posts = posts;
    this.session = session;
    this.postId = post?.id ?? null;
    this.isCreate = post === null;
    this.editing = this.isCreate;
    this.name = post?.name ?? "";
    this.description = post?.description ?? "";
    this.mealDrafts = this.isCreate ? [this.newDraft()] : [];

    makeAutoObservable<this, "posts" | "session" | "nextDraftId">(this, {
      postId: false,
      isCreate: false,
      posts: false,
      session: false,
      nextDraftId: false,
    });
  }

  private newDraft(): MealDraft {
    return emptyDraft(this.nextDraftId--);
  }

  get post(): PostRead | null {
    if (this.postId === null) return null;
    return this.posts.items.find((p) => p.id === this.postId) ?? null;
  }

  get meals(): MealRead[] {
    return this.post?.meals ?? [];
  }

  get nameError(): string | null {
    return validatePostName(this.name);
  }

  get descriptionError(): string | null {
    return validatePostDescription(this.description);
  }

  mealErrors(draft: MealDraft): MealDraftErrors {
    return {
      name: validateMealName(draft.name),
      cal: validateMealMacro(draft.cal, "Калории"),
      protein: validateMealMacro(draft.protein, "Белки"),
      fat: validateMealMacro(draft.fat, "Жиры"),
      carbohydrate: validateMealMacro(draft.carbohydrate, "Углеводы"),
    };
  }

  get isValid(): boolean {
    if (this.nameError || this.descriptionError) return false;
    return this.mealDrafts.every((draft) => {
      const errors = this.mealErrors(draft);
      return (
        !errors.name &&
        !errors.cal &&
        !errors.protein &&
        !errors.carbohydrate &&
        !errors.fat
      );
    });
  }

  setName(value: string): void {
    this.name = value;
  }

  setDescription(value: string): void {
    this.description = value;
  }

  updateMealDraft(id: number, patch: Partial<MealDraft>): void {
    this.mealDrafts = this.mealDrafts.map((d) =>
      d.id === id ? { ...d, ...patch } : d,
    );
  }

  addMealDraft(): void {
    if (this.mealDrafts.length >= MAX_POST_MEALS) return;
    this.mealDrafts = [...this.mealDrafts, this.newDraft()];
  }

  removeMealDraft(id: number): void {
    if (this.mealDrafts.length <= MIN_POST_MEALS) return;
    this.mealDrafts = this.mealDrafts.filter((d) => d.id !== id);

    if (id in this.photoFiles) {
      const { [id]: _removed, ...rest } = this.photoFiles;
      this.photoFiles = rest;
    }
    const url = this.photoPreviews[id];
    if (url) {
      URL.revokeObjectURL(url);
      const { [id]: _removed, ...rest } = this.photoPreviews;
      this.photoPreviews = rest;
    }
  }

  selectMealPhoto(mealId: number, file: File): void {
    const previews = { ...this.photoPreviews };
    const old = previews[mealId];
    if (old) URL.revokeObjectURL(old);
    previews[mealId] = URL.createObjectURL(file);
    this.photoPreviews = previews;
    this.photoFiles = { ...this.photoFiles, [mealId]: file };
  }

  private resetPhotoDrafts(): void {
    revokePreviews(this.photoPreviews);
    this.photoPreviews = {};
    this.photoFiles = {};
  }

  startEdit(): void {
    if (!this.post) return;
    this.name = this.post.name;
    this.description = this.post.description ?? "";
    this.mealDrafts = this.meals.map(toDraft);
    this.resetPhotoDrafts();
    this.error = null;
    this.submitted = false;
    this.confirmingCancelEdit = false;
    this.editing = true;
  }

  cancelEdit(): void {
    this.resetPhotoDrafts();
    this.submitted = false;
    this.confirmingCancelEdit = false;
    this.editing = false;
  }

  beginCancelEdit(): void {
    if (this.pending) return;
    this.confirmingCancelEdit = true;
  }

  dismissCancelEdit(): void {
    this.confirmingCancelEdit = false;
  }

  beginClose(): boolean {
    if (this.pending) return false;
    if (this.editing) {
      this.confirmingClose = true;
      return false;
    }
    return true;
  }

  dismissClose(): void {
    this.confirmingClose = false;
  }

  requestDelete(): void {
    this.confirmingDelete = true;
  }

  dismissDelete(): void {
    this.confirmingDelete = false;
  }

  dispose(): void {
    revokePreviews(this.photoPreviews);
  }

  async handleDelete(onClose: () => void): Promise<void> {
    await runAsync(
      this,
      async () => {
        await this.posts.deletePost(this.post!.id);
        onClose();
      },
      {
        before: () => {
          this.pending = true;
        },
        after: () => {
          this.pending = false;
        },
        fallbackMessage: "Не удалось удалить",
      },
    );
    if (this.error) {
      runInAction(() => {
        this.confirmingDelete = false;
      });
    }
  }

  async handleUpdate(): Promise<void> {
    if (!this.isValid) {
      this.submitted = true;
      return;
    }
    const postId = this.post!.id;
    const previousMealIds = new Set(this.meals.map((m) => m.id));

    await runAsync(
      this,
      async () => {
        for (const [mealId, file] of Object.entries(this.photoFiles)) {
          const id = Number(mealId);
          if (id < 0) continue;
          await this.posts.setMealPicture(postId, id, file);
        }

        const payload: PostWrite = {
          auth_id: this.post!.auth_id,
          name: this.name,
          description: this.description || null,
          mark: this.post!.mark,
          comment: this.post!.comment,
          meals: this.mealDrafts.map(toMealWrite),
        };
        const updated = await this.posts.updatePost(postId, payload);

        const newDrafts = this.mealDrafts.filter((d) => d.id < 0);
        if (newDrafts.length > 0) {
          const newlyCreatedMeals = (updated.meals ?? []).filter(
            (m) => !previousMealIds.has(m.id),
          );
          for (const [index, newDraft] of newDrafts.entries()) {
            const file = this.photoFiles[newDraft.id];
            const createdMeal = newlyCreatedMeals[index];
            if (file && createdMeal) {
              await this.posts.setMealPicture(postId, createdMeal.id, file);
            }
          }
        }

        runInAction(() => {
          this.resetPhotoDrafts();
          this.editing = false;
        });
      },
      {
        before: () => {
          this.pending = true;
        },
        after: () => {
          this.pending = false;
        },
        fallbackMessage: "Не удалось сохранить",
      },
    );
  }

  async handleCreate(onClose: () => void): Promise<void> {
    if (!this.isValid) {
      this.submitted = true;
      return;
    }
    await runAsync(
      this,
      async () => {
        const payload: PostWrite = {
          auth_id: this.session.user!.auth_id,
          name: this.name,
          description: this.description || null,
          meals: this.mealDrafts.map(toMealWrite),
        };
        const created = await this.posts.createPost(payload);

        for (const [index, draft] of this.mealDrafts.entries()) {
          const file = this.photoFiles[draft.id];
          const createdMeal = created.meals?.[index];
          if (file && createdMeal) {
            await this.posts.setMealPicture(created.id, createdMeal.id, file);
          }
        }

        this.resetPhotoDrafts();
        onClose();
      },
      {
        before: () => {
          this.pending = true;
        },
        after: () => {
          this.pending = false;
        },
        fallbackMessage: "Не удалось создать пост",
      },
    );
  }
}
