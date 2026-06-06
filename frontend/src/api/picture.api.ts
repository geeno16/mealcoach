import { ApiError } from "./client";

export interface PictureRead {
  id: number;
  post_id: number | null;
  updated_at: string;
  created_at: string;
}

async function handleBinaryResponse(response: Response): Promise<Blob> {
  if (!response.ok) {
    throw new ApiError(response.status, response.statusText);
  }
  return response.blob();
}

async function handleJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new ApiError(response.status, response.statusText);
  }
  return response.json() as Promise<T>;
}

export const pictureApi = {
  getPicture(id: number): Promise<Blob> {
    return fetch(`/api/picture/${id}`).then(handleBinaryResponse);
  },

  uploadPicture(formData: FormData): Promise<PictureRead> {
    return fetch("/api/picture", { method: "POST", body: formData }).then(
      (res) => handleJsonResponse<PictureRead>(res),
    );
  },

  updatePicture(id: number, formData: FormData): Promise<PictureRead> {
    return fetch(`/api/picture/${id}`, {
      method: "PUT",
      body: formData,
    }).then((res) => handleJsonResponse<PictureRead>(res));
  },

  deletePicture(id: number): Promise<void> {
    return fetch(`/api/picture/${id}`, { method: "DELETE" }).then(
      async (res) => {
        if (!res.ok) throw new ApiError(res.status, res.statusText);
      },
    );
  },
};
