import { makeAutoObservable, runInAction } from "mobx";

import { type UserWrite } from "../../api";
import { runAsync } from "../../shared/runAsync";
import {
  validateAge,
  validateHeight,
  validateUserName,
  validateUserSurname,
  validateWeight,
} from "../../shared/validation";
import { type SessionStore } from "../auth/session.store";

export class ProfileEditStore {
  editing = false;
  name = "";
  surname = "";
  age = "";
  weight = "";
  height = "";
  pending = false;
  error: string | null = null;
  submitted = false;

  private readonly session: SessionStore;

  constructor(session: SessionStore) {
    this.session = session;
    makeAutoObservable<this, "session">(this, { session: false });
  }

  get nameError(): string | null {
    return validateUserName(this.name);
  }

  get surnameError(): string | null {
    return validateUserSurname(this.surname);
  }

  get ageError(): string | null {
    return validateAge(this.age);
  }

  get weightError(): string | null {
    return validateWeight(this.weight);
  }

  get heightError(): string | null {
    return validateHeight(this.height);
  }

  get isValid(): boolean {
    return (
      !this.nameError &&
      !this.surnameError &&
      !this.ageError &&
      !this.weightError &&
      !this.heightError
    );
  }

  setName(value: string): void {
    this.name = value;
  }

  setSurname(value: string): void {
    this.surname = value;
  }

  setAge(value: string): void {
    this.age = value;
  }

  setWeight(value: string): void {
    this.weight = value;
  }

  setHeight(value: string): void {
    this.height = value;
  }

  startEdit(): void {
    const user = this.session.user;
    if (!user) return;
    this.name = user.name;
    this.surname = user.surname ?? "";
    this.age = user.age?.toString() ?? "";
    this.weight = user.weight?.toString() ?? "";
    this.height = user.height?.toString() ?? "";
    this.error = null;
    this.submitted = false;
    this.editing = true;
  }

  cancelEdit(): void {
    this.submitted = false;
    this.editing = false;
  }

  async save(): Promise<void> {
    const user = this.session.user;
    if (!user) return;
    if (!this.isValid) {
      this.submitted = true;
      return;
    }

    await runAsync(
      this,
      async () => {
        const payload: UserWrite = {
          ...user,
          name: this.name,
          surname: this.surname || null,
          age: this.age ? Number(this.age) : null,
          weight: this.weight ? Number(this.weight) : null,
          height: this.height ? Number(this.height) : null,
        };
        await this.session.updateUser(payload);
        runInAction(() => {
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
}
