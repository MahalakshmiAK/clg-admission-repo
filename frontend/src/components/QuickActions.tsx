// src/components/QuickActions.tsx
// Preset query chips shown above the chat — preserved from the original UI.

import styles from './QuickActions.module.css'

const QUICK_QUERIES = [
  { label: 'IIT Madras fees', query: 'What is the fee structure at IIT Madras?' },
  { label: 'NIT Trichy docs', query: 'What documents do I need for NIT Trichy?' },
  { label: 'JEE deadlines', query: 'When is the JEE Advanced registration deadline?' },
  { label: 'BITS Pilani cutoff', query: 'What is the BITSAT cutoff for BITS Pilani?' },
]

interface Props {
  onSelect: (query: string) => void
  disabled: boolean
}

export function QuickActions({ onSelect, disabled }: Props) {
  return (
    <div className={styles.strip}>
      {QUICK_QUERIES.map(({ label, query }) => (
        <button
          key={label}
          className={styles.chip}
          onClick={() => onSelect(query)}
          disabled={disabled}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
