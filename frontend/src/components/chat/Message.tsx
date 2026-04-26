import ReactMarkdown from 'react-markdown'
import type { Message as MessageType } from '../../types'
import { SocraticBadge } from './SocraticBadge'

export function Message({ message }: { message: MessageType }) {
  const isUser = message.role === 'user'
  const level = message.socratic_level ?? 0
  return (
    <div
      style={{
        alignSelf: isUser ? 'flex-end' : 'flex-start',
        background: isUser ? 'var(--bg-raised)' : 'var(--bg-surface)',
        borderLeft: isUser ? undefined : `3px solid var(--socratic-${level})`,
        borderRadius: 8,
        padding: 12,
        maxWidth: '80%',
        position: 'relative',
      }}
    >
      {!isUser && (
        <div style={{ position: 'absolute', top: 6, right: 6 }}>
          <SocraticBadge level={level as 0 | 1 | 2 | 3 | 4} />
        </div>
      )}
      {isUser ? <span>{message.content}</span> : <ReactMarkdown>{message.content}</ReactMarkdown>}
      {!isUser && message.vault_citation && (
        <details>
          <summary>Vault citation</summary>
          <small>{message.vault_citation}</small>
        </details>
      )}
    </div>
  )
}
