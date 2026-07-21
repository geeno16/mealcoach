export { authApi } from "../features/auth/auth.api";
export { apiClient, ApiError } from "./client";
export { notificationsApi } from "../features/notifications/notifications.api";
export { pictureApi } from "../features/posts/picture.api";
export { postsApi } from "../features/posts/posts.api";
export { statisticsApi } from "../features/stats/statistics.api";
export { usersApi } from "./users.api";

export type {
  AuthRead,
  AuthWrite,
  EmailVerify,
} from "../features/auth/auth.api";
export type { PictureRead } from "../features/posts/picture.api";
export type {
  NotificationRead,
  NotificationType,
} from "../features/notifications/notifications.api";
export type {
  MealRead,
  MealWrite,
  PostRead,
  PostWrite,
} from "../features/posts/posts.api";
export type {
  DailyPoint,
  MacroRatio,
  MarkStats,
  MealStats,
  NutritionStats,
  PostStats,
  ProfileStats,
  StatisticsRead,
} from "../features/stats/statistics.api";
export type { UserRead, UserRole, UserWrite } from "./users.api";
