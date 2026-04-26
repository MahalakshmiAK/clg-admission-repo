// src/types/index.ts
// Shared TypeScript interfaces. Mirror the backend Pydantic schemas exactly
// so any breaking API change surfaces immediately as a type error.

/** A single retrieved source document. */
export interface Source {
  title: string | null
  college: string | null
  score: number
}

/** POST /api/v1/chat request body. */
export interface ChatRequest {
  query: string
  top_k?: number
}

/** POST /api/v1/chat response body. */
export interface ChatResponse {
  answer: string
  sources: Source[]
}

/** A single message displayed in the chat UI. */
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  sources?: Source[]
  isLoading?: boolean
}
