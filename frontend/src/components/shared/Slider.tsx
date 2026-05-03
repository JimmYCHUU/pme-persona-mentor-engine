/** Slider — shared slider component. Stub wrapper. */
export function Slider(props: React.InputHTMLAttributes<HTMLInputElement>) {
    return <input type="range" {...props} style={{ width: '100%', accentColor: 'var(--accent)', ...props.style }} />
}
