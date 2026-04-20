import { BASE_URL as BASE, defaultHeaders as headers, handleResponse } from './client'

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
