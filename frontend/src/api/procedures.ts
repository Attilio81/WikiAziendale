const BASE = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}`
const API_KEY = import.meta.env.VITE_API_KEY ?? 'dev-change-me'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export interface Procedure {
  id: string
  titolo: string
  categoria: string | null
  contenuto_md: string
  autore: string | null
  tags: string[]
  created_at: string
  updated_at: string
  version: number
  compilation_status: 'pending' | 'compiled' | 'failed'
  compilation_error: string | null
}

export interface ProcedureCreate {
  titolo: string
  categoria?: string
  contenuto_md: string
  autore?: string
  tags?: string[]
}

export interface ProcedureListResponse {
  items: Procedure[]
  total: number
  page: number
  page_size: number
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export async function fetchProcedures(params?: {
  q?: string
  categoria?: string
  compilation_status?: string
  page?: number
  page_size?: number
}): Promise<ProcedureListResponse> {
  const qs = new URLSearchParams()
  if (params?.q) qs.set('q', params.q)
  if (params?.categoria) qs.set('categoria', params.categoria)
  if (params?.compilation_status) qs.set('compilation_status', params.compilation_status)
  if (params?.page) qs.set('page', String(params.page))
  if (params?.page_size) qs.set('page_size', String(params.page_size))
  const res = await fetch(`${BASE}/procedures/?${qs}`, { headers })
  return handleResponse(res)
}

export async function fetchProcedure(id: string): Promise<Procedure> {
  const res = await fetch(`${BASE}/procedures/${id}`, { headers })
  return handleResponse(res)
}

export async function createProcedure(data: ProcedureCreate): Promise<Procedure> {
  const res = await fetch(`${BASE}/procedures/`, {
    method: 'POST',
    headers,
    body: JSON.stringify(data),
  })
  return handleResponse(res)
}

export async function updateProcedure(id: string, data: Partial<ProcedureCreate>): Promise<Procedure> {
  const res = await fetch(`${BASE}/procedures/${id}`, {
    method: 'PUT',
    headers,
    body: JSON.stringify(data),
  })
  return handleResponse(res)
}

export async function deleteProcedure(id: string): Promise<void> {
  const res = await fetch(`${BASE}/procedures/${id}`, { method: 'DELETE', headers })
  return handleResponse(res)
}
