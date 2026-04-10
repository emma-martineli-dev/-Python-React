import type { AlertItem, FileItem, Page } from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, { cache: "no-store", ...init });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  files: {
    list: (offset = 0, limit = 20) =>
      request<Page<FileItem>>(`/files?offset=${offset}&limit=${limit}`),

    get: (id: string) =>
      request<FileItem>(`/files/${id}`),

    create: (title: string, file: File) => {
      const form = new FormData();
      form.append("title", title);
      form.append("file", file);
      return request<FileItem>("/files", { method: "POST", body: form });
    },

    update: (id: string, title: string) =>
      request<FileItem>(`/files/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title }),
      }),

    delete: (id: string) =>
      request<void>(`/files/${id}`, { method: "DELETE" }),

    downloadUrl: (id: string) => `${BASE_URL}/files/${id}/download`,
  },

  alerts: {
    list: (offset = 0, limit = 20) =>
      request<Page<AlertItem>>(`/alerts?offset=${offset}&limit=${limit}`),
  },
};
