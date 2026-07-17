export { authApi } from "./auth.api";
export { apiClient, ApiError } from "./client";
export { notificationsApi } from "./notifications.api";
export { pictureApi } from "./picture.api";
export { postsApi } from "./posts.api";
export { statisticsApi } from "./statistics.api";
export { usersApi } from "./users.api";

export type { AuthRead, AuthWrite, EmailVerify } from "./auth.api";
export type { PictureRead } from "./picture.api";
export type { NotificationRead, NotificationType } from "./notifications.api";
export type { MealRead, MealWrite, PostRead, PostWrite } from "./posts.api";
export type {
  DailyPoint,
  MacroRatio,
  MarkStats,
  MealStats,
  NutritionStats,
  PostStats,
  ProfileStats,
  StatisticsRead,
} from "./statistics.api";
export type { UserRead, UserRole, UserWrite } from "./users.api";
