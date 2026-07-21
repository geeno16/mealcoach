import { makeAutoObservable } from "mobx";

import { SessionStore } from "../features/auth/session.store";
import { NotificationStore } from "../features/notifications/notification.store";
import { PostsStore } from "../features/posts/posts.store";
import { CoachStore } from "../features/trainees/coach.store";

export class RootStore {
  session: SessionStore;
  coach: CoachStore;
  notifications: NotificationStore;
  posts: PostsStore;

  constructor() {
    this.session = new SessionStore();
    this.coach = new CoachStore();
    this.notifications = new NotificationStore();
    this.posts = new PostsStore();
    makeAutoObservable(this, {
      session: false,
      coach: false,
      notifications: false,
      posts: false,
    });
  }
}

export const rootStore = new RootStore();
