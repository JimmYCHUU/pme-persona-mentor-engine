import * as RadixSlider from '@radix-ui/react-slider'

export function Slider({
	value,
	min = 0,
	max = 100,
	onChange,
}: {
	value: number
	min?: number
	max?: number
	onChange: (value: number) => void
}) {
	return (
		<RadixSlider.Root value={[value]} min={min} max={max} onValueChange={(v) => onChange(v[0] ?? value)}>
			<RadixSlider.Track style={{ height: 6, background: 'var(--bg-overlay)' }}>
				<RadixSlider.Range style={{ height: 6, background: 'var(--accent)' }} />
			</RadixSlider.Track>
			<RadixSlider.Thumb style={{ width: 16, height: 16, borderRadius: 999, background: 'var(--accent)' }} />
		</RadixSlider.Root>
	)
}
