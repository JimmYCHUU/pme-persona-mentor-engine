export function StepRoadmap({ next_steps }: { next_steps: string[] }) {
  return (
    <ol>
      {next_steps.map((step, idx) => (
        <li key={idx}>{step}</li>
      ))}
    </ol>
  )
}
