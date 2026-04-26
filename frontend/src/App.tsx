// src/App.tsx
// Root component. Composes layout from smaller, single-responsibility components.
// All data flow passes through the useChat hook — App itself holds no fetch logic.

import { useEffect, useRef } from 'react'
import { useChat } from './hooks/useChat'
import { ChatMessage } from './components/ChatMessage'
import { ChatInput } from './components/ChatInput'
import { QuickActions } from './components/QuickActions'
import styles from './App.module.css'

export default function App() {
  const { messages, isLoading, sendMessage } = useChat()
  const bottomRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to the latest message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className={styles.shell}>
      <div className={styles.container}>

        {/* ── Header ──────────────────────────────────────────────────── */}
        <header className={styles.header}>
          <h1 className={styles.title}>College Admission Assistant</h1>
          <p className={styles.subtitle}>
            RAG-powered guidance · IITs · NITs · BITS · VIT
          </p>
        </header>

        {/* ── Quick action chips ───────────────────────────────────────── */}
        <QuickActions onSelect={sendMessage} disabled={isLoading} />

        {/* ── Message list ─────────────────────────────────────────────── */}
        <main className={styles.chatBox} aria-live="polite" aria-label="Chat messages">
          {messages.map(msg => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={bottomRef} />
        </main>

        {/* ── Input bar ────────────────────────────────────────────────── */}
        <ChatInput onSend={sendMessage} isLoading={isLoading} />

      </div>
    </div>
  )
}
