import { apiClient } from "./client";
import { type components } from "./schema.gen";

export type PostWrite = components["schemas"]["PostWrite"];
export type PostRead = components["schemas"]["PostRead"];

export const postsApi = {
  async getPost(id: number): Promise<PostRead> {
    const { data: result } = await apiClient.GET("/api/posts/{id}", {
      params: { path: { id } },
    });
    return result!;
  },

  async getAllByAuth(authId: number): Promise<PostRead[]> {
    const { data: result } = await apiClient.GET("/api/posts", {
      params: { query: { auth_id: authId } },
    });
    return result!;
  },

  async createPost(data: PostWrite): Promise<PostRead> {
    const { data: result } = await apiClient.POST("/api/posts", { body: data });
    return result!;
  },

  async updatePost(id: number, data: PostWrite): Promise<PostRead> {
    const { data: result } = await apiClient.PUT("/api/posts/{id}", {
      params: { path: { id } },
      body: data,
    });
    return result!;
  },

  async deletePost(id: number): Promise<void> {
    await apiClient.DELETE("/api/posts/{id}", {
      params: { path: { id } },
    });
  },
};
