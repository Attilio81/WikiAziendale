import { BASE_URL as BASE, defaultHeaders as headers, handleResponse } from './client'

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

export async function uploadProcedure(file: File, categoria?: string, autore?: string): Promise<Procedure> {
  const formData = new FormData()
  formData.append('file', file)
  if (categoria) formData.append('categoria', categoria)
  if (autore) formData.append('autore', autore)
  const res = await fetch(`${BASE}/procedures/upload`, {
    method: 'POST',
    headers: { 'X-API-Key': headers['X-API-Key'] },
    body: formData,
  })
  return handleResponse<Procedure>(res)
}
