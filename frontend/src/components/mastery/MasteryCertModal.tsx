import { motion } from 'framer-motion'
import type { MasteryCertificate } from '../../types'
import { Button } from '../shared/Button'

export function MasteryCertModal({ cert, onClose }: { cert: MasteryCertificate; onClose: () => void }) {
  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'grid', placeItems: 'center' }}>
      <motion.div initial={{ y: 30, opacity: 0 }} animate={{ y: 0, opacity: 1 }} style={{ background: 'var(--bg-surface)', border: '1px solid var(--accent)', borderRadius: 12, width: 560, padding: 24 }}>
        <h2>{cert.concept_label}</h2>
        <p>{cert.mentor_statement}</p>
        <small>{JSON.stringify(cert.evidence_summary)}</small>
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 8, marginTop: 10 }}>
          <Button variant='ghost' onClick={onClose}>Close</Button>
          <Button onClick={() => window.print()}>Export as PDF</Button>
        </div>
      </motion.div>
    </div>
  )
}
