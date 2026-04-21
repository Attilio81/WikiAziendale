import { BASE_URL, defaultHeaders, handleResponse } from './client'

export interface ChatResponse {
  answer: string
  sources: string[]
  session_id: string
}

export async function sendMessage(
  message: string,
  session_id: string,
): Promise<ChatResponse> {
  const res = await fetch(`${BASE_URL}/chat/`, {
    method: 'POST',
    headers: defaultHeaders,
    body: JSON.stringify({ message, session_id }),
  })
  return handleResponse<ChatResponse>(res)
}
