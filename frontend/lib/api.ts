export type ApiError = {
  status: number;
  message: string;
  detail?: unknown;
};

export async function apiGet<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    method: "GET",
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const data = await res.json();
      msg = data?.error || data?.message || msg;
      throw { status: res.status, message: msg, detail: data } as ApiError;
    } catch {
      throw { status: res.status, message: msg } as ApiError;
    }
  }
  return (await res.json()) as T;
}

export async function apiPost<T>(path: string, body?: unknown, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "content-type": "application/json", ...(init?.headers || {}) },
    body: JSON.stringify(body ?? {}),
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    let msg = res.statusText;
    try {
      const data = await res.json();
      msg = data?.error || data?.message || msg;
      throw { status: res.status, message: msg, detail: data } as ApiError;
    } catch {
      throw { status: res.status, message: msg } as ApiError;
    }
  }
  return (await res.json()) as T;
}
