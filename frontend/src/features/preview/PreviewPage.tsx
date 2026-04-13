import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { generatePreview } from '../../lib/api'
import {
  ArrowLeft,
  Layers,
  GitBranch,
  BarChart2,
  Pencil,
  Check,
  ChevronRight,
} from 'lucide-react'

type Tab = 'sitemap' | 'flows' | 'complexity'

type Screen = { id: string; name: string; purpose: string; svg: string }
type Flow = { persona_id: string; persona_name: string; node_count: number }
type Complexity = {
  tier: 'simple' | 'moderate' | 'complex'
  screen_count: number
  feature_count: number
  effort_weeks: string
  scope_reduction_suggestions: string[]
}

type PreviewData = {
  screens: Screen[]
  user_flows: Flow[]
  complexity: Complexity
}

const TIER_COLORS: Record<string, { bg: string; text: string; border: string; label: string }> = {
  simple: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200', label: 'Simple' },
  moderate: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200', label: 'Moderate' },
  complex: { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200', label: 'Complex' },
}

// ──────────────────────────────────────────────
// Skeleton
// ──────────────────────────────────────────────

function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-3 animate-pulse">
      <div className="h-4 bg-gray-100 rounded w-1/3" />
      <div className="h-3 bg-gray-100 rounded w-2/3" />
      <div className="h-32 bg-gray-100 rounded-lg w-full" />
    </div>
  )
}

// ──────────────────────────────────────────────
// Placeholder wireframe (when no SVG)
// ──────────────────────────────────────────────

function WireframePlaceholder({ name }: { name: string }) {
  return (
    <div className="h-40 bg-gray-50 rounded-lg p-3 flex flex-col gap-2 border border-gray-100">
      {/* Nav bar */}
      <div className="flex items-center gap-1.5">
        <div className="w-2 h-2 rounded-full bg-gray-200" />
        <div className="h-2 bg-gray-200 rounded flex-1" />
        <div className="w-8 h-2 bg-gray-200 rounded" />
      </div>
      {/* Hero block */}
      <div className="h-10 bg-gray-200 rounded" />
      {/* Content blocks */}
      <div className="flex gap-1.5 flex-1">
        <div className="flex-1 bg-gray-200 rounded" />
        <div className="flex-1 bg-gray-200 rounded" />
        <div className="flex-1 bg-gray-200 rounded" />
      </div>
      {/* Label */}
      <p className="text-gray-400 text-xs text-center mt-1">{name}</p>
    </div>
  )
}

// ──────────────────────────────────────────────
// Sitemap tab
// ──────────────────────────────────────────────

function SitemapTab({
  screens,
  editMode,
  edits,
  onEdit,
}: {
  screens: Screen[]
  editMode: boolean
  edits: Record<string, string>
  onEdit: (id: string, value: string) => void
}) {
  if (screens.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <Layers size={32} className="mx-auto mb-2 opacity-40" />
        <p className="text-sm">No screens generated</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {screens.map((screen) => (
        <div
          key={screen.id}
          className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-medium text-gray-900 text-sm">{screen.name}</h3>
            {editMode ? (
              <textarea
                className="mt-1.5 w-full text-xs text-gray-600 rounded-lg border border-indigo-200 bg-indigo-50 px-2 py-1.5 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400"
                rows={2}
                value={edits[screen.id] ?? screen.purpose}
                onChange={(e) => onEdit(screen.id, e.target.value)}
              />
            ) : (
              <p className="text-xs text-gray-500 mt-0.5">{edits[screen.id] ?? screen.purpose}</p>
            )}
          </div>
          {screen.svg ? (
            <div
              className="p-3 bg-gray-50 overflow-hidden"
              style={{ maxHeight: '240px' }}
              dangerouslySetInnerHTML={{ __html: screen.svg }}
            />
          ) : (
            <div className="p-3 bg-gray-50">
              <WireframePlaceholder name={screen.name} />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

// ──────────────────────────────────────────────
// Flows tab
// ──────────────────────────────────────────────

const FLOW_NODES = ['TRIGGER', 'SCREEN', 'ACTION', 'OUTCOME']

function FlowCard({
  flow,
  editMode,
  note,
  onNoteChange,
}: {
  flow: Flow
  editMode: boolean
  note: string
  onNoteChange: (v: string) => void
}) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <button
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0">
            <span className="text-purple-600 font-semibold text-xs">
              {flow.persona_name.charAt(0).toUpperCase()}
            </span>
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">{flow.persona_name}</p>
            <p className="text-xs text-gray-500">{flow.node_count} steps in this flow</p>
          </div>
        </div>
        <ChevronRight
          size={16}
          className={`text-gray-400 transition-transform ${expanded ? 'rotate-90' : ''}`}
        />
      </button>

      {expanded && (
        <div className="px-4 pb-4 space-y-3">
          {/* Visual node chain */}
          <div className="flex items-center gap-1 flex-wrap">
            {FLOW_NODES.map((node, i) => (
              <div key={node} className="flex items-center gap-1">
                <div className="px-2.5 py-1 rounded-lg border text-xs font-semibold bg-purple-50 border-purple-200 text-purple-700">
                  {node}
                </div>
                {i < FLOW_NODES.length - 1 && (
                  <span className="text-gray-300 text-xs">→</span>
                )}
              </div>
            ))}
          </div>

          <p className="text-xs text-gray-400 italic">
            {flow.node_count} nodes in flow
          </p>

          {editMode && (
            <div>
              <label className="block text-xs font-semibold text-gray-500 mb-1 uppercase tracking-wide">
                Add notes for this flow
              </label>
              <textarea
                className="w-full text-xs text-gray-700 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400"
                rows={2}
                placeholder="Add context or notes about this user flow..."
                value={note}
                onChange={(e) => onNoteChange(e.target.value)}
              />
            </div>
          )}

          {!editMode && note && (
            <div className="bg-indigo-50 border border-indigo-100 rounded-lg px-3 py-2">
              <p className="text-xs text-indigo-700">{note}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Complexity tab
// ──────────────────────────────────────────────

function ComplexityTab({
  complexity,
  editMode,
  overrideNote,
  onOverrideChange,
  extraSuggestions,
}: {
  complexity: Complexity
  editMode: boolean
  overrideNote: string
  onOverrideChange: (v: string) => void
  extraSuggestions: string[]
}) {
  const tierKey = complexity.tier ?? 'moderate'
  const colors = TIER_COLORS[tierKey] ?? TIER_COLORS['moderate']
  const allSuggestions = [...(complexity.scope_reduction_suggestions ?? []), ...extraSuggestions]

  return (
    <div className="space-y-4">
      {/* Tier card */}
      <div className={`rounded-xl border p-5 ${colors.bg} ${colors.border}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className={`text-xs font-semibold uppercase tracking-wide ${colors.text} opacity-70`}>
              Complexity Tier
            </p>
            <p className={`text-2xl font-black ${colors.text} mt-1`}>
              {colors.label}
            </p>
          </div>
          <div
            className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors.bg} border ${colors.border}`}
          >
            <BarChart2 size={22} className={colors.text} />
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Screens', value: complexity.screen_count, icon: '🖥️' },
          { label: 'Features', value: complexity.feature_count, icon: '⚙️' },
          { label: 'Est. Timeline', value: complexity.effort_weeks, icon: '📅' },
        ].map((stat) => (
          <div
            key={stat.label}
            className="bg-white rounded-xl border border-gray-200 p-4 text-center shadow-sm"
          >
            <p className="text-xl mb-1">{stat.icon}</p>
            <p className="text-lg font-bold text-gray-900 leading-tight">{stat.value ?? '—'}</p>
            <p className="text-xs text-gray-500 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Scope reduction suggestions */}
      {allSuggestions.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
          <h3 className="font-semibold text-gray-900 text-sm mb-3">Scope Reduction Tips</h3>
          <ul className="space-y-2">
            {allSuggestions.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-indigo-400 mt-0.5 flex-shrink-0">•</span>
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Edit mode override */}
      {editMode && (
        <div>
          <label className="block text-xs font-semibold text-gray-500 mb-1.5 uppercase tracking-wide">
            Override scope notes
          </label>
          <textarea
            className="w-full text-sm text-gray-700 rounded-lg border border-indigo-200 bg-indigo-50 px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400"
            rows={3}
            placeholder="Add custom scope reduction notes — will be appended to the list above"
            value={overrideNote}
            onChange={(e) => onOverrideChange(e.target.value)}
          />
        </div>
      )}
    </div>
  )
}

// ──────────────────────────────────────────────
// Main page
// ──────────────────────────────────────────────

export default function PreviewPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<Tab>('sitemap')
  const [editMode, setEditMode] = useState(false)

  // Edit state
  const [screenEdits, setScreenEdits] = useState<Record<string, string>>({})
  const [flowNotes, setFlowNotes] = useState<Record<string, string>>({})
  const [complexityOverride, setComplexityOverride] = useState('')
  const [extraSuggestions, setExtraSuggestions] = useState<string[]>([])

  // Edited data flags (for badge display)
  const [editedTabs, setEditedTabs] = useState<Set<Tab>>(new Set())

  const { data, isLoading, error } = useQuery<PreviewData>({
    queryKey: ['preview', sessionId],
    queryFn: () => generatePreview(sessionId!),
    enabled: !!sessionId,
    staleTime: Infinity,
    retry: 1,
  })

  const handleApplyChanges = () => {
    const newEdited = new Set(editedTabs)
    if (Object.keys(screenEdits).length > 0) newEdited.add('sitemap')
    if (Object.keys(flowNotes).some((k) => flowNotes[k])) newEdited.add('flows')
    if (complexityOverride.trim()) {
      newEdited.add('complexity')
      setExtraSuggestions(
        complexityOverride
          .split('\n')
          .map((s) => s.trim())
          .filter(Boolean),
      )
    }
    setEditedTabs(newEdited)
    setEditMode(false)
  }

  const tabs: { key: Tab; label: string; icon: React.ReactNode }[] = [
    { key: 'sitemap', label: 'Site Map', icon: <Layers size={14} /> },
    { key: 'flows', label: 'User Flows', icon: <GitBranch size={14} /> },
    { key: 'complexity', label: 'Complexity', icon: <BarChart2 size={14} /> },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 sticky top-0 z-10">
        <button
          onClick={() => navigate(-1)}
          className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft size={18} className="text-gray-600" />
        </button>
        <div className="flex-1">
          <h1 className="font-semibold text-gray-900 text-sm">App Preview</h1>
          <p className="text-xs text-gray-500">Review your app structure</p>
        </div>

        <div className="flex items-center gap-2">
          {data && (
            <span className="text-xs text-gray-400 hidden sm:block">
              {data.screens.length} screens
            </span>
          )}
          {data && (
            <button
              onClick={() => {
                if (editMode) {
                  handleApplyChanges()
                } else {
                  setEditMode(true)
                }
              }}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all ${
                editMode
                  ? 'bg-indigo-600 border-indigo-600 text-white'
                  : 'bg-white border-gray-200 text-gray-600 hover:border-indigo-300 hover:text-indigo-600'
              }`}
            >
              {editMode ? (
                <>
                  <Check size={12} />
                  Apply Changes
                </>
              ) : (
                <>
                  <Pencil size={12} />
                  Edit
                </>
              )}
            </button>
          )}
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 px-4">
        <div className="max-w-2xl mx-auto flex gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`relative flex items-center gap-1.5 px-3 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab.key
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.icon}
              {tab.label}
              {editedTabs.has(tab.key) && (
                <span className="text-xs ml-0.5 opacity-70">✏️</span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full">
        {isLoading && (
          <div className="space-y-4">
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
            <p className="text-red-700 font-medium text-sm">Preview generation failed</p>
            <p className="text-red-500 text-xs mt-1">
              {error instanceof Error ? error.message : 'Unknown error'}
            </p>
            <button
              onClick={() => navigate('/')}
              className="mt-3 text-sm text-red-600 underline"
            >
              Start over
            </button>
          </div>
        )}

        {data && (
          <>
            {activeTab === 'sitemap' && (
              <SitemapTab
                screens={data.screens}
                editMode={editMode}
                edits={screenEdits}
                onEdit={(id, val) => setScreenEdits((prev) => ({ ...prev, [id]: val }))}
              />
            )}

            {activeTab === 'flows' && (
              <div className="space-y-3">
                {!data.user_flows || data.user_flows.length === 0 ? (
                  <div className="text-center py-16 text-gray-400">
                    <GitBranch size={32} className="mx-auto mb-2 opacity-40" />
                    <p className="text-sm">No user flows defined</p>
                  </div>
                ) : (
                  data.user_flows.map((flow, i) => (
                    <FlowCard
                      key={flow.persona_id ?? i}
                      flow={flow}
                      editMode={editMode}
                      note={flowNotes[flow.persona_id ?? String(i)] ?? ''}
                      onNoteChange={(v) =>
                        setFlowNotes((prev) => ({
                          ...prev,
                          [flow.persona_id ?? String(i)]: v,
                        }))
                      }
                    />
                  ))
                )}
              </div>
            )}

            {activeTab === 'complexity' && data.complexity && (
              <ComplexityTab
                complexity={data.complexity}
                editMode={editMode}
                overrideNote={complexityOverride}
                onOverrideChange={setComplexityOverride}
                extraSuggestions={extraSuggestions}
              />
            )}
          </>
        )}
      </div>

      {/* Bottom CTA */}
      <div className="bg-white border-t border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          <button
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg px-4 py-3 transition-colors disabled:opacity-50"
            onClick={() => navigate(`/compile/${sessionId}`)}
            disabled={isLoading || !!error}
          >
            Build Prompt →
          </button>
        </div>
      </div>
    </div>
  )
}
