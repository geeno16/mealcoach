import { makeAutoObservable, runInAction } from "mobx";

import {
  ApiError,
  authApi,
  usersApi,
  type AuthRead,
  type AuthWrite,
  type EmailVerify,
  type UserRead,
  type UserWrite,
} from "../../api";

export type SessionStatus = "loading" | "ready";

export class SessionStore {
  auth: AuthRead | null = null;
  user: UserRead | null = null;
  status: SessionStatus = "loading";

  constructor() {
    makeAutoObservable(this);
    void this.init();
  }

  get isAuthenticated(): boolean {
    return this.auth !== null;
  }

  get hasProfile(): boolean {
    return this.user !== null;
  }

  get awaitingCoach(): boolean {
    return (
      this.user !== null &&
      this.user.role === "trainee" &&
      this.user.coach_id === null
    );
  }

  async init(): Promise<void> {
    try {
      const auth = await authApi.me();
      runInAction(() => {
        this.auth = auth;
      });
      await this.loadUser();
    } catch {
      runInAction(() => {
        this.auth = null;
        this.user = null;
      });
    } finally {
      runInAction(() => {
        this.status = "ready";
      });
    }
  }

  async loadUser(): Promise<void> {
    if (!this.auth) return;
    try {
      const user = await usersApi.getUser(this.auth.id);
      runInAction(() => {
        this.user = user;
      });
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        runInAction(() => {
          this.user = null;
        });
        return;
      }
      throw error;
    }
  }

  async register(data: AuthWrite): Promise<void> {
    await authApi.register(data);
  }

  async resendCode(data: AuthWrite): Promise<void> {
    await authApi.resendCode(data);
  }

  async verifyEmail(data: EmailVerify): Promise<void> {
    await authApi.verifyEmail(data);
  }

  async forgotPassword(email: string): Promise<void> {
    await authApi.forgotPassword({ email });
  }

  async resetPassword(
    email: string,
    code: string,
    password: string,
  ): Promise<void> {
    await authApi.resetPassword({ email, code, password });
  }

  async login(data: AuthWrite): Promise<void> {
    const auth = await authApi.login(data);
    runInAction(() => {
      this.auth = auth;
    });
    await this.loadUser();
  }

  async createUser(data: UserWrite): Promise<void> {
    const user = await usersApi.createUser(data);
    runInAction(() => {
      this.user = user;
    });
  }

  async updateUser(data: UserWrite): Promise<void> {
    const user = await usersApi.updateUser(data.auth_id, data);
    runInAction(() => {
      this.user = user;
    });
  }

  async requestCoach(coachEmail: string): Promise<void> {
    if (!this.user) return;
    const user = await usersApi.requestCoach(this.user.auth_id, coachEmail);
    runInAction(() => {
      this.user = user;
    });
  }

  async clearCoach(): Promise<void> {
    if (!this.user) return;
    await usersApi.deleteCoach(this.user.auth_id);
    await this.loadUser();
  }

  async logout(): Promise<void> {
    await authApi.logout();
    runInAction(() => {
      this.auth = null;
      this.user = null;
    });
  }
}
