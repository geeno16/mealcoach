import { makeAutoObservable } from "mobx";

import { type UserRole, type UserWrite } from "../../api";
import { runAsync } from "../../shared/runAsync";
import {
  validateAge,
  validateEmail,
  validateHeight,
  validateUserName,
  validateUserSurname,
  validateWeight,
} from "../../shared/validation";

import { type SessionStore } from "./session.store";

export class ForkFormStore {
  role: UserRole = "trainee";
  name = "";
  surname = "";
  age = "";
  weight = "";
  height = "";
  coachEmail = "";
  pending = false;
  error: string | null = null;
  submitted = false;

  private readonly session: SessionStore;

  constructor(session: SessionStore) {
    this.session = session;
    makeAutoObservable<this, "session">(this, { session: false });
  }

  get isTrainee(): boolean {
    return this.role === "trainee";
  }

  get nameError(): string | null {
    return validateUserName(this.name);
  }

  get surnameError(): string | null {
    return validateUserSurname(this.surname);
  }

  get ageError(): string | null {
    return this.isTrainee ? validateAge(this.age) : null;
  }

  get weightError(): string | null {
    return this.isTrainee ? validateWeight(this.weight) : null;
  }

  get heightError(): string | null {
    return this.isTrainee ? validateHeight(this.height) : null;
  }

  get coachEmailError(): string | null {
    if (!this.isTrainee) return null;
    if (!this.coachEmail) return "Email тренера обязателен";
    return validateEmail(this.coachEmail, "Email тренера");
  }

  get isValid(): boolean {
    return (
      !this.nameError &&
      !this.surnameError &&
      !this.ageError &&
      !this.weightError &&
      !this.heightError &&
      !this.coachEmailError
    );
  }

  setRole(role: UserRole): void {
    this.role = role;
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

  setCoachEmail(value: string): void {
    this.coachEmail = value;
  }

  async submit(): Promise<boolean> {
    if (!this.session.auth) return false;
    if (!this.isValid) {
      this.submitted = true;
      return false;
    }

    const payload: UserWrite = {
      auth_id: this.session.auth.id,
      role: this.role,
      name: this.name,
    };
    if (this.surname) payload.surname = this.surname;
    if (this.isTrainee) {
      if (this.age) payload.age = Number(this.age);
      if (this.weight) payload.weight = Number(this.weight);
      if (this.height) payload.height = Number(this.height);
      if (this.coachEmail) payload.coach_email = this.coachEmail;
    }

    let created = false;
    await runAsync(
      this,
      async () => {
        await this.session.createUser(payload);
        created = true;
      },
      {
        before: () => {
          this.pending = true;
        },
        after: () => {
          this.pending = false;
        },
        fallbackMessage: "Не удалось создать профиль",
      },
    );
    return created;
  }
}
