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

  async getPostPictures(postId: number): Promise<number[]> {
    const { data: result } = await apiClient.GET(
      "/api/posts/{post_id}/pictures",
      {
        params: { path: { post_id: postId } },
      },
    );
    return result!;
  },

  async createPostPicture(postId: number, data: Blob): Promise<PictureRead> {
    const { data: result } = await apiClient.POST(
      "/api/posts/{post_id}/pictures",
      {
        params: { path: { post_id: postId } },
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

  async updatePicture(id: number, data: Blob): Promise<void> {
    await apiClient.PUT("/api/pictures/{id}", {
      params: { path: { id } },
      body: data,
      bodySerializer: (body) => body,
    });
  },

  async deletePicture(id: number): Promise<void> {
    await apiClient.DELETE("/api/pictures/{id}", { params: { path: { id } } });
  },
};
