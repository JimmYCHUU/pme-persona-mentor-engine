import type { PropsWithChildren } from 'react'
import type { ButtonHTMLAttributes } from 'react'

type Variant = 'primary' | 'ghost'

export function Button({ children, variant = 'primary', ...props }: PropsWithChildren<{ variant?: Variant } & ButtonHTMLAttributes<HTMLButtonElement>>) {
  const style =
    variant === 'primary'
      ? {
          background: 'var(--accent)',
          color: 'var(--bg-base)',
          border: '1px solid var(--accent)',
        }
      : {
          background: 'transparent',
          color: 'var(--accent)',
          border: '1px solid var(--accent)',
        }
  return (
    <button
      {...props}
      style={{
        ...style,
        borderRadius: 'var(--radius-md)',
        padding: '8px 12px',
        fontFamily: 'var(--font-sans)',
        cursor: 'pointer',
      }}
    >
      {children}
    </button>
  )
}
