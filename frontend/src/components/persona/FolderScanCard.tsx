/**
 * FolderScanCard — confirmation UI when a folder scan completes.
 * Shows detected files, inferred mentor, and confirmation/disambiguation controls.
 */

import { useState } from 'react'

interface ScanResult {
    status: 'empty' | 'config_found' | 'detected' | 'ambiguous' | 'multiple_people'
    files: string[]
    file_count: number
    detected_person: string | null
    confidence: number
}

interface Props {
    scan: ScanResult
    onConfirm: (personaName: string, files: string[]) => void
    onCancel: () => void
}

export function FolderScanCard({ scan, onConfirm, onCancel }: Props) {
    const [nameOverride, setNameOverride] = useState(scan.detected_person || '')

    const confidenceLabel = scan.confidence >= 0.8 ? 'High' : scan.confidence >= 0.5 ? 'Medium' : 'Low'
    const confidenceColor = scan.confidence >= 0.8 ? 'var(--success)' : scan.confidence >= 0.5 ? 'var(--warning)' : 'var(--danger)'

    return (
        <div style={{
            padding: '24px',
            background: 'var(--bg-raised)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '12px',
            maxWidth: '520px',
        }}>
            <h3 style={{
                fontFamily: 'var(--font-display)',
                fontSize: '20px', fontWeight: 400,
                marginBottom: '16px',
            }}>
                Folder Scan Results
            </h3>

            {/* File count */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '12px 16px', marginBottom: '12px',
                background: 'var(--bg-surface)', borderRadius: '8px',
                fontSize: '13px',
            }}>
                <span style={{ color: 'var(--text-secondary)' }}>Files found</span>
                <span style={{ color: 'var(--accent-bright)', fontFamily: 'var(--font-mono)' }}>
                    {scan.file_count}
                </span>
            </div>

            {/* Status-specific content */}
            {scan.status === 'empty' && (
                <p style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '16px' }}>
                    No supported files found in this folder.
                </p>
            )}

            {(scan.status === 'config_found' || scan.status === 'detected') && scan.detected_person && (
                <div style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    padding: '12px 16px', marginBottom: '12px',
                    background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
                    borderRadius: '8px', fontSize: '13px',
                }}>
                    <span style={{ color: 'var(--text-secondary)' }}>Detected mentor</span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ color: 'var(--accent-bright)', fontWeight: 500 }}>
                            {scan.detected_person}
                        </span>
                        <span style={{
                            fontSize: '10px', padding: '2px 6px', borderRadius: '4px',
                            background: confidenceColor, color: 'var(--bg-base)',
                            fontWeight: 600, textTransform: 'uppercase',
                        }}>
                            {confidenceLabel}
                        </span>
                    </div>
                </div>
            )}

            {(scan.status === 'ambiguous' || scan.status === 'multiple_people') && (
                <div style={{ marginBottom: '16px' }}>
                    <label style={{
                        display: 'block', fontSize: '13px', fontWeight: 500,
                        color: 'var(--text-secondary)', marginBottom: '6px',
                    }}>
                        {scan.status === 'multiple_people'
                            ? 'Multiple people detected — who should this mentor be?'
                            : 'Who are these files for?'}
                    </label>
                    <input
                        value={nameOverride}
                        onChange={e => setNameOverride(e.target.value)}
                        placeholder="Enter mentor name…"
                        style={{
                            width: '100%', padding: '10px 14px',
                            background: 'var(--bg-surface)', border: '1px solid var(--border-default)',
                            borderRadius: '8px', color: 'var(--text-primary)',
                            fontFamily: 'var(--font-body)', fontSize: '14px', outline: 'none',
                        }}
                    />
                </div>
            )}

            {/* File list preview */}
            {scan.files.length > 0 && (
                <details style={{ marginBottom: '16px' }}>
                    <summary style={{
                        fontSize: '12px', color: 'var(--text-muted)', cursor: 'pointer',
                        fontFamily: 'var(--font-mono)', userSelect: 'none',
                    }}>
                        View files ({scan.files.length})
                    </summary>
                    <div style={{ maxHeight: '160px', overflow: 'auto', marginTop: '8px' }}>
                        {scan.files.map((f, i) => (
                            <div key={i} style={{
                                fontSize: '12px', color: 'var(--text-secondary)',
                                padding: '4px 0', fontFamily: 'var(--font-mono)',
                            }}>
                                {f.split('/').pop()}
                            </div>
                        ))}
                    </div>
                </details>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
                <button onClick={onCancel} style={{
                    flex: 1, padding: '10px',
                    background: 'transparent', border: '1px solid var(--border-default)',
                    borderRadius: '8px', color: 'var(--text-muted)',
                    fontFamily: 'var(--font-body)', fontSize: '13px',
                    cursor: 'pointer',
                }}>
                    Cancel
                </button>
                <button
                    onClick={() => onConfirm(nameOverride || scan.detected_person || '', scan.files)}
                    disabled={!nameOverride && !scan.detected_person}
                    style={{
                        flex: 2, padding: '10px',
                        background: 'var(--accent-glow)', border: '1px solid var(--border-accent)',
                        borderRadius: '8px', color: 'var(--accent-bright)',
                        fontFamily: 'var(--font-body)', fontSize: '13px', fontWeight: 500,
                        cursor: !nameOverride && !scan.detected_person ? 'not-allowed' : 'pointer',
                        opacity: !nameOverride && !scan.detected_person ? 0.5 : 1,
                    }}
                >
                    Ingest these files
                </button>
            </div>
        </div>
    )
}
