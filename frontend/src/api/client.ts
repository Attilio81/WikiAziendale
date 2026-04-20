const BASE = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}`
const API_KEY = import.meta.env.VITE_API_KEY ?? 'dev-change-me'

export const BASE_URL = BASE

export const defaultHeaders = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}
