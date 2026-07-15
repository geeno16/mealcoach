import { makeAutoObservable } from "mobx";

import { CoachStore } from "../stores/coach.store";
import { SessionStore } from "../stores/session.store";

export class RootStore {
  session: SessionStore;
  coach: CoachStore;

  constructor() {
    this.session = new SessionStore();
    this.coach = new CoachStore();
    makeAutoObservable(this, { session: false, coach: false });
  }
}

export const rootStore = new RootStore();
