// src/components/ChatMessage.tsx
// Renders a single message bubble. Handles user, assistant, and system roles.
// Sources are shown as a collapsible section below the assistant answer.

import { useState } from 'react'
import type { Message } from '../types'
import styles from './ChatMessage.module.css'

interface Props {
  message: Message
}

/** Very small markdown → HTML: bold and line breaks only. */
function formatMarkdown(text: string): string {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br />')
}

export function ChatMessage({ message }: Props) {
  const [sourcesOpen, setSourcesOpen] = useState(false)
  const hasSources = (message.sources ?? []).length > 0

  if (message.isLoading) {
    return (
      <div className={`${styles.bubble} ${styles.assistant}`}>
        <span className={styles.dots}>
          <span /><span /><span />
        </span>
      </div>
    )
  }

  return (
    <div className={`${styles.bubble} ${styles[message.role]}`}>
      {/* Render formatted markdown safely */}
      <div
        className={styles.content}
        dangerouslySetInnerHTML={{ __html: formatMarkdown(message.content) }}
      />

      {hasSources && (
        <div className={styles.sourcesWrapper}>
          <button
            className={styles.sourcesToggle}
            onClick={() => setSourcesOpen(o => !o)}
          >
            {sourcesOpen ? '▲ Hide sources' : `▼ ${message.sources!.length} sources`}
          </button>

          {sourcesOpen && (
            <ul className={styles.sourceList}>
              {message.sources!.map((s, i) => (
                <li key={i} className={styles.sourceItem}>
                  <span className={styles.sourceTitle}>{s.title ?? 'Untitled'}</span>
                  <span className={styles.sourceMeta}>
                    {s.college} · score {s.score.toFixed(2)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
