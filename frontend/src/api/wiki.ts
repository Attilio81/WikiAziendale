const BASE = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}`
const API_KEY = import.meta.env.VITE_API_KEY ?? 'dev-change-me'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export interface WikiPageListItem {
  id: string
  slug: string
  titolo: string
  last_compiled_at: string | null
  compilation_model: string | null
  version: number
  source_raw_ids: string[] | null
}

export interface WikiPageRead extends WikiPageListItem {
  contenuto_md: string
  links: string[] | null
}

export interface WikiIndexRead {
  id: number
  tree_md: string | null
  last_rebuilt_at: string | null
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export async function fetchWikiPages(): Promise<WikiPageListItem[]> {
  const res = await fetch(`${BASE}/wiki/pages`, { headers })
  return handleResponse(res)
}

export async function fetchWikiPage(slug: string): Promise<WikiPageRead> {
  const res = await fetch(`${BASE}/wiki/pages/${encodeURIComponent(slug)}`, { headers })
  return handleResponse(res)
}

export async function fetchWikiIndex(): Promise<WikiIndexRead> {
  const res = await fetch(`${BASE}/wiki/index`, { headers })
  return handleResponse(res)
}
