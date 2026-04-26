// src/api/client.ts
// Centralised API client. All fetch calls go through here.
// The base URL is read from the VITE_API_BASE_URL env variable.
// In development, Vite's proxy rewrites /api → http://127.0.0.1:8000/api,
// so VITE_API_BASE_URL is not needed locally.

import type { ChatRequest, ChatResponse } from '../types'

// In dev the proxy handles /api, so we use a relative path.
// In a production build VITE_API_BASE_URL is the deployed backend URL.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

/** POST /api/v1/chat */
export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/v1/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    // Surface the FastAPI error detail if present
    const err = await res.json().catch(() => ({}))
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }

  return res.json() as Promise<ChatResponse>
}

/** GET /api/v1/health */
export async function getHealth(): Promise<{ status: string; engine: string }> {
  const res = await fetch(`${API_BASE}/api/v1/health`)
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`)
  return res.json()
}
