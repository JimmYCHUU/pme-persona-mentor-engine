import * as Slider from '@radix-ui/react-slider'
import { useEffect, useMemo, useState } from 'react'
import { usePersonaStore } from '../../store/personaStore'

export function SliderPanel() {
  const { sliders, updateSliders } = usePersonaStore()
  const [local, setLocal] = useState({
    abrasiveness: Number(sliders.abrasiveness ?? 50),
    proactivity: Number(sliders.proactivity ?? 50),
    explainDepth: Number(sliders.explainDepth ?? 50),
  })

  useEffect(() => {
    const id = setTimeout(() => {
      void updateSliders(local)
    }, 500)
    return () => clearTimeout(id)
  }, [local])

  const Label = ({ v }: { v: number }) => <span>{v === 0 ? 'Gentle Professor' : v === 100 ? 'Drill Sergeant' : v}</span>

  const renderSlider = (key: 'abrasiveness' | 'proactivity' | 'explainDepth', label: string) => (
    <div key={key}>
      <label>{label}: <Label v={local[key]} /></label>
      <Slider.Root value={[local[key]]} min={0} max={100} onValueChange={(v) => setLocal((s) => ({ ...s, [key]: v[0] ?? 0 }))}>
        <Slider.Track style={{ height: 6, background: 'var(--bg-overlay)' }}>
          <Slider.Range style={{ background: 'var(--accent)', height: 6 }} />
        </Slider.Track>
        <Slider.Thumb style={{ width: 16, height: 16, background: 'var(--accent)', borderRadius: 999 }} />
      </Slider.Root>
    </div>
  )

  return <div style={{ display: 'grid', gap: 12 }}>{renderSlider('abrasiveness', 'Abrasiveness')}{renderSlider('proactivity', 'Proactivity')}{renderSlider('explainDepth', 'Explain Depth')}</div>
}
