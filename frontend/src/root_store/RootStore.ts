import { makeAutoObservable } from "mobx";

import { CoachStore } from "../stores/coach.store";
import { NotificationStore } from "../stores/notification.store";
import { PostsStore } from "../stores/posts.store";
import { SessionStore } from "../stores/session.store";

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
