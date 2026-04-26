import { useState } from 'react'
import { api } from '../../api/client'
import { usePersonaStore } from '../../store/personaStore'
import { Button } from '../shared/Button'
import { FileUpload } from '../shared/FileUpload'
import { SliderPanel } from './SliderPanel'

export function PersonaBuilder() {
  const [step, setStep] = useState(1)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [urls, setUrls] = useState('')
  const [personaId, setPersonaId] = useState('')
  const { setActive } = usePersonaStore()
  const [gapQuestions, setGapQuestions] = useState<string[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const next = () => setStep((s) => Math.min(5, s + 1))
  const prev = () => setStep((s) => Math.max(1, s - 1))

  const complete = async () => {
    const id = personaId || crypto.randomUUID()
    const profile = { persona_id: id, name, description, soul: {}, sliders: { abrasiveness: 50, proactivity: 50, explainDepth: 50 } }
    await api.createPersona(profile)
    setPersonaId(id)
    setActive(id)
    for (const url of urls.split('\n').map((s) => s.trim()).filter(Boolean)) {
      await api.ingestFingerprint(url, id)
    }
    const q = await fetch(`http://localhost:8000/persona/${id}/gap-questions`).then((r) => r.json())
    setGapQuestions(q.data.questions ?? [])
    setStep(5)
  }

  const submitGaps = async () => {
    await fetch(`http://localhost:8000/persona/${personaId}/gap-fill-answers`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(answers),
    })
    setStep(1)
  }

  return (
    <div style={{ padding: 12, border: '1px solid var(--bg-overlay)', borderRadius: 8 }}>
      <div>Step {step}/5</div>
      {step === 1 && (
        <div>
          <input value={name} onChange={(e) => setName(e.target.value)} placeholder='Mentor name' />
          <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder='Description' />
          <Button onClick={next} disabled={!name || !description}>Next</Button>
        </div>
      )}
      {step === 2 && (
        <div>
          <textarea value={urls} onChange={(e) => setUrls(e.target.value)} placeholder='One public URL per line' />
          <Button variant='ghost' onClick={prev}>Back</Button>
          <Button onClick={next}>Next</Button>
        </div>
      )}
      {step === 3 && (
        <div>
          <FileUpload personaId={personaId || 'pending'} />
          <Button variant='ghost' onClick={prev}>Back</Button>
          <Button onClick={next}>Next</Button>
        </div>
      )}
      {step === 4 && (
        <div>
          <SliderPanel />
          <Button variant='ghost' onClick={prev}>Back</Button>
          <Button onClick={() => void complete()}>Complete</Button>
        </div>
      )}
      {step === 5 && (
        <div>
          {gapQuestions.length === 0 && <div>Interview pending</div>}
          {gapQuestions.map((q) => (
            <label key={q}>
              {q}
              <input value={answers[q] ?? ''} onChange={(e) => setAnswers((a) => ({ ...a, [q]: e.target.value }))} />
            </label>
          ))}
          <Button onClick={() => void submitGaps()}>Submit</Button>
        </div>
      )}
    </div>
  )
}
