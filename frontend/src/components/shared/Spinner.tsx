/** Spinner — loading indicator. */
export function Spinner({ size = 20 }: { size?: number }) {
    return (
        <div style={{
            width: size,
            height: size,
            border: `2px solid var(--bg-overlay)`,
            borderTopColor: 'var(--accent)',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
        }}>
            <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
        </div>
    )
}
