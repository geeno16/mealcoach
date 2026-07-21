import { apiClient } from "../../api/client";
import { type components } from "../../api/schema.gen";

export type AuthWrite = components["schemas"]["AuthWrite"];
export type AuthRead = components["schemas"]["AuthRead"];
export type EmailVerify = components["schemas"]["EmailVerify"];
export type PasswordForgot = components["schemas"]["PasswordForgot"];
export type PasswordReset = components["schemas"]["PasswordReset"];

export const authApi = {
  async me(): Promise<AuthRead> {
    const { data: result } = await apiClient.GET("/api/auth/me");
    return result!;
  },

  async register(data: AuthWrite): Promise<AuthRead> {
    const { data: result } = await apiClient.POST("/api/auth", { body: data });
    return result!;
  },

  async verifyEmail(data: EmailVerify): Promise<AuthRead> {
    const { data: result } = await apiClient.POST("/api/auth/verify-email", {
      body: data,
    });
    return result!;
  },

  async resendCode(data: AuthWrite): Promise<void> {
    await apiClient.POST("/api/auth/resend-code", { body: data });
  },

  async forgotPassword(data: PasswordForgot): Promise<void> {
    await apiClient.POST("/api/auth/forgot-password", { body: data });
  },

  async resetPassword(data: PasswordReset): Promise<AuthRead> {
    const { data: result } = await apiClient.POST("/api/auth/reset-password", {
      body: data,
    });
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
