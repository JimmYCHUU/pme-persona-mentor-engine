/** FileUpload — drag-and-drop file upload component. Stub for Phase 2. */
export function FileUpload({ onUpload }: { onUpload?: (file: File) => void }) {
    return (
        <div style={{
            border: '1px dashed var(--accent-dim)',
            borderRadius: 'var(--radius-lg)',
            padding: '24px',
            textAlign: 'center',
            color: 'var(--text-muted)',
            fontSize: '0.85rem',
            cursor: 'pointer',
        }}>
            <p>Drop files here or click to upload</p>
            <input
                type="file"
                style={{ display: 'none' }}
                onChange={(e) => e.target.files?.[0] && onUpload?.(e.target.files[0])}
            />
        </div>
    )
}
