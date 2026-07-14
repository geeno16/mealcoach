import { apiClient } from "./client";
import { type components } from "./schema.gen";

export type PictureRead = components["schemas"]["PictureRead"];

export const pictureApi = {
  async getPicture(id: number): Promise<Blob> {
    const { data: result } = await apiClient.GET("/api/pictures/{id}", {
      params: { path: { id } },
      parseAs: "blob",
    });
    return result!;
  },

  async setMealPicture(mealId: number, data: Blob): Promise<PictureRead> {
    const { data: result } = await apiClient.PUT(
      "/api/meals/{meal_id}/picture",
      {
        params: { path: { meal_id: mealId } },
        body: data,
        bodySerializer: (body) => body,
      },
    );
    return result!;
  },

  async setAvatar(userId: number, data: Blob): Promise<PictureRead> {
    const { data: result } = await apiClient.PUT(
      "/api/users/{user_id}/avatar",
      {
        params: { path: { user_id: userId } },
        body: data,
        bodySerializer: (body) => body,
      },
    );
    return result!;
  },

  async deletePicture(id: number): Promise<void> {
    await apiClient.DELETE("/api/pictures/{id}", { params: { path: { id } } });
  },
};
