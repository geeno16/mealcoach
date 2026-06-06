import createClient, { type Middleware } from "openapi-fetch";

import { type paths } from "./schema.gen";

function extractMessage(body: unknown): string {
  if (typeof body !== "object" || body === null) return "Unknown error";

  const detail = (body as Record<string, unknown>).detail;

  if (typeof detail === "string") return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as Record<string, unknown>;
    return typeof first.msg === "string" ? first.msg : "Validation error";
  }

  return "Unknown error";
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const errorMiddleware: Middleware = {
  async onResponse({ response }) {
    if (!response.ok) {
      let message = response.statusText;
      try {
        const body: unknown = await response.clone().json();
        message = extractMessage(body);
      } catch {
        // тело не распарсилось — оставляем statusText
      }
      throw new ApiError(response.status, message);
    }
  },
};

export const apiClient = createClient<paths>({ baseUrl: "" });
apiClient.use(errorMiddleware);
