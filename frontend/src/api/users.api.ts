import { apiClient } from "./client";
import { type components } from "./schema.gen";

export type UserRole = components["schemas"]["UserRole"];
export type UserWrite = components["schemas"]["UserWrite"];
export type UserRead = components["schemas"]["UserRead"];

export const usersApi = {
  async getUser(id: number): Promise<UserRead> {
    const { data: result } = await apiClient.GET("/api/users/{id}", {
      params: { path: { id } },
    });
    return result!;
  },

  async getAllByCoach(coachId: number): Promise<UserRead[]> {
    const { data: result } = await apiClient.GET("/api/users", {
      params: { query: { coach_id: coachId } },
    });
    return result!;
  },

  async createUser(data: UserWrite): Promise<UserRead> {
    const { data: result } = await apiClient.POST("/api/users", { body: data });
    return result!;
  },

  async updateUser(id: number, data: UserWrite): Promise<UserRead> {
    const { data: result } = await apiClient.PUT("/api/users/{id}", {
      params: { path: { id } },
      body: data,
    });
    return result!;
  },

  async getRequests(coachId: number): Promise<UserRead[]> {
    const { data: result } = await apiClient.GET("/api/users/{id}/requests", {
      params: { path: { id: coachId } },
    });
    return result!;
  },

  async requestCoach(id: number, coachEmail: string): Promise<UserRead> {
    const { data: result } = await apiClient.POST(
      "/api/users/{id}/request-coach",
      {
        params: { path: { id } },
        body: { coach_email: coachEmail },
      },
    );
    return result!;
  },

  async approveRequest(traineeId: number): Promise<UserRead> {
    const { data: result } = await apiClient.POST("/api/users/{id}/approve", {
      params: { path: { id: traineeId } },
    });
    return result!;
  },

  async deleteCoach(traineeId: number): Promise<void> {
    await apiClient.DELETE("/api/users/{id}/coach", {
      params: { path: { id: traineeId } },
    });
  },
};
