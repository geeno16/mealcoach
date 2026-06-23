import { apiClient } from "./client";
import { type components } from "./schema.gen";

export type AuthWrite = components["schemas"]["AuthWrite"];
export type AuthRead = components["schemas"]["AuthRead"];

export const authApi = {
  async register(data: AuthWrite): Promise<AuthRead> {
    const { data: result } = await apiClient.POST("/api/auth", { body: data });
    return result!;
  },

  async login(data: AuthWrite): Promise<AuthRead> {
    const { data: result } = await apiClient.POST("/api/auth/login", {
      body: data,
    });
    return result!;
  },

  async logout(): Promise<void> {
    await apiClient.POST("/api/auth/logout");
  },

  async update(id: number, data: AuthWrite): Promise<AuthRead> {
    const { data: result } = await apiClient.PUT("/api/auth/{id}", {
      params: { path: { id } },
      body: data,
    });
    return result!;
  },

  async delete(id: number): Promise<void> {
    await apiClient.DELETE("/api/auth/{id}", {
      params: { path: { id } },
    });
  },
};
