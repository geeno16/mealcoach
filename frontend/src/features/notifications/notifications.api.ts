import { apiClient } from "../../api/client";
import { type components } from "../../api/schema.gen";

export type NotificationRead = components["schemas"]["NotificationRead"];
export type NotificationType = components["schemas"]["NotificationType"];

export const notificationsApi = {
  async getNotifications(): Promise<NotificationRead[]> {
    const { data: result } = await apiClient.GET("/api/notifications");
    return result!;
  },
};
