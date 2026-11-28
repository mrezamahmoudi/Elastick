// Thin API client for the Elastick backend.
// The optional X-API-Key is kept in localStorage and attached to every call;
// a 401 anywhere triggers a global event so the App can show the key prompt.

const KEY_STORAGE = 'elastick-api-key'

export function getApiKey(): string {
  return localStorage.getItem(KEY_STORAGE) ?? ''
}

export function setApiKey(key: string): void {
  if (key) localStorage.setItem(KEY_STORAGE, key)
  else localStorage.removeItem(KEY_STORAGE)
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function api<T = any>(path: string, init?: RequestInit): Promise<T> {
  const body = init?.body
  const res = await fetch(path, {
    ...init,
    headers: {
      ...(init?.headers ?? {}),
      ...(getApiKey() ? { 'X-API-Key': getApiKey() } : {}),
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
  })

  if (res.status === 401) {
    window.dispatchEvent(new Event('elastick:unauthorized'))
    throw new ApiError(401, 'Unauthorized — a valid X-API-Key is required.')
  }

  if (!res.ok) {
    let detail = res.statusText
    try {
      const parsed = await res.json()
      detail = parsed?.detail ?? JSON.stringify(parsed)
    } catch {
      /* keep statusText */
    }
    throw new ApiError(res.status, detail)
  }

  return res.json()
}
