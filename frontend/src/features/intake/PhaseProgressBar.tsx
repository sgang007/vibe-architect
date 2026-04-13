import type { Phase } from '../../lib/store'

const PHASES: { key: Phase; label: string }[] = [
  { key: 'IDEA', label: 'Idea' },
  { key: 'TOUCHPOINTS', label: 'Users' },
  { key: 'FEATURES', label: 'Features' },
  { key: 'TECHNICAL', label: 'Technical' },
]

const PHASE_ORDER: Phase[] = [
  'IDLE',
  'IDEA',
  'TOUCHPOINTS',
  'FEATURES',
  'TECHNICAL',
  'EXTRACTING',
  'ENRICHED',
  'PREVIEWING',
  'READY',
]

export default function PhaseProgressBar({
  phase,
  progressPct,
}: {
  phase: Phase
  progressPct: number
}) {
  const currentIdx = PHASE_ORDER.indexOf(phase)

  return (
    <div className="bg-white border-b border-gray-100 px-4 py-2">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-1 mb-1.5">
          {PHASES.map((p, i) => {
            const phaseIdx = PHASE_ORDER.indexOf(p.key)
            const isDone = currentIdx > phaseIdx
            const isActive = currentIdx === phaseIdx
            return (
              <div key={p.key} className="flex items-center flex-1">
                <div
                  className={`flex-1 h-1.5 rounded-full transition-all duration-500 ${
                    isDone ? 'bg-blue-500' : isActive ? 'bg-blue-300' : 'bg-gray-200'
                  }`}
                />
                {i < PHASES.length - 1 && <div className="w-1" />}
              </div>
            )
          })}
        </div>
        <div className="flex justify-between">
          {PHASES.map((p) => {
            const phaseIdx = PHASE_ORDER.indexOf(p.key)
            const isDone = currentIdx > phaseIdx
            const isActive = currentIdx === phaseIdx
            return (
              <span
                key={p.key}
                className={`text-xs ${
                  isDone || isActive ? 'text-blue-600 font-medium' : 'text-gray-400'
                }`}
              >
                {p.label}
              </span>
            )
          })}
        </div>
        {progressPct > 0 && (
          <div className="mt-1.5 h-0.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-blue-400 rounded-full transition-all duration-700"
              style={{ width: `${progressPct}%` }}
            />
          </div>
        )}
      </div>
    </div>
  )
}
