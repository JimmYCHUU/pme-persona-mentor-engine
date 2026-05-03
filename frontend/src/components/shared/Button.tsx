/** Button — shared button component. */
import type { ButtonHTMLAttributes, ReactNode } from 'react'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'ghost'
    children: ReactNode
}

export function Button({ variant = 'primary', children, className, ...props }: Props) {
    return (
        <button className={`btn btn-${variant} ${className || ''}`} {...props}>
            {children}
        </button>
    )
}
