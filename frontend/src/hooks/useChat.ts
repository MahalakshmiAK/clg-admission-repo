// src/hooks/useChat.ts
// Encapsulates all chat state and API interaction.
// Components stay pure — they receive state + handlers, never call fetch directly.

import { useState, useCallback } from 'react'
import { sendChat } from '../api/client'
import type { Message, Source } from '../types'

/** Generate a simple unique ID for each message. */
const uid = () => Math.random().toString(36).slice(2, 9)

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: uid(),
      role: 'system',
      content: 'Hello! Ask me anything about engineering college admissions in India.',
    },
  ])
  const [isLoading, setIsLoading] = useState(false)

  const sendMessage = useCallback(async (query: string) => {
    if (!query.trim() || isLoading) return

    // 1. Append user message immediately
    const userMsg: Message = { id: uid(), role: 'user', content: query }
    setMessages(prev => [...prev, userMsg])
    setIsLoading(true)

    // 2. Append a loading placeholder
    const loadingId = uid()
    setMessages(prev => [
      ...prev,
      { id: loadingId, role: 'assistant', content: '', isLoading: true },
    ])

    try {
      // 3. Call the typed API client
      const data = await sendChat({ query, top_k: 5 })

      // 4. Replace placeholder with real response
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? { id: loadingId, role: 'assistant', content: data.answer, sources: data.sources }
            : m
        )
      )
    } catch (err) {
      const detail = err instanceof Error ? err.message : 'Unknown error'
      setMessages(prev =>
        prev.map(m =>
          m.id === loadingId
            ? {
                id: loadingId,
                role: 'system',
                content: `Connection error: ${detail}. Is the backend running?`,
              }
            : m
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [isLoading])

  return { messages, isLoading, sendMessage }
}
