// src/components/ChatInput.tsx
// Controlled input with send button. Disabled while a request is in-flight.

import { useState, type KeyboardEvent } from 'react'
import styles from './ChatInput.module.css'

interface Props {
  onSend: (query: string) => void
  isLoading: boolean
}

export function ChatInput({ onSend, isLoading }: Props) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || isLoading) return
    onSend(trimmed)
    setValue('')
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className={styles.inputArea}>
      <input
        type="text"
        className={styles.input}
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about fees, deadlines, eligibility…"
        maxLength={500}
        disabled={isLoading}
        aria-label="Your question"
      />
      <button
        className={styles.sendBtn}
        onClick={handleSend}
        disabled={isLoading || !value.trim()}
        aria-label="Send message"
      >
        {isLoading ? '…' : 'Send'}
      </button>
    </div>
  )
}
