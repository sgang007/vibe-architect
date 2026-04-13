import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Clock, Zap, Eye, X, User } from 'lucide-react'
import { getUser, getHistory, type HistoryEntry } from '../../lib/auth'

const PLATFORM_COLORS: Record<string, string> = {
  replit: 'bg-orange-100 text-orange-700 border-orange-200',
  bolt: 'bg-purple-100 text-purple-700 border-purple-200',
  lovable: 'bg-pink-100 text-pink-700 border-pink-200',
  v0: 'bg-gray-100 text-gray-700 border-gray-200',
  cursor: 'bg-blue-100 text-blue-700 border-blue-200',
  emergent: 'bg-teal-100 text-teal-700 border-teal-200',
}

function PlatformBadge({ platform }: { platform: string }) {
  const colors = PLATFORM_COLORS[platform.toLowerCase()] ?? 'bg-gray-100 text-gray-600 border-gray-200'
  return (
    <span className={`px-2 py-0.5 rounded-full border text-xs font-semibold capitalize ${colors}`}>
      {platform}
    </span>
  )
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return iso
  }
}

function formatTokens(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

function PromptModal({ entry, onClose }: { entry: HistoryEntry; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h3 className="font-semibold text-gray-900 text-sm">{entry.appName || 'Prompt'}</h3>
            <div className="flex items-center gap-2 mt-1">
              <PlatformBadge platform={entry.platform} />
              <span className="text-xs text-gray-400">{formatDate(entry.timestamp)}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
          >
            <X size={16} />
          </button>
        </div>

        {/* Prompt */}
        <div className="flex-1 overflow-y-auto bg-gray-950 rounded-b-2xl">
          <pre className="text-xs text-gray-200 font-mono p-6 whitespace-pre-wrap break-words leading-relaxed">
            {entry.prompt}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default function HistoryPage() {
  const navigate = useNavigate()
  const user = getUser()
  const history = getHistory()
  const [activeEntry, setActiveEntry] = useState<HistoryEntry | null>(null)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 sticky top-0 z-10">
        <button
          onClick={() => navigate('/')}
          className="flex items-center gap-1.5 p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft size={16} />
          <span className="text-sm font-medium hidden sm:block">Back</span>
        </button>
        <div className="flex-1">
          <h1 className="font-semibold text-gray-900 text-sm">Prompt History</h1>
          {user && (
            <p className="text-xs text-gray-500">{user.email}</p>
          )}
        </div>
        {user && (
          <div className="flex items-center gap-1.5 text-xs text-gray-500">
            <User size={13} />
            <span className="hidden sm:block">{user.name}</span>
          </div>
        )}
      </header>

      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Not logged in */}
        {!user && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-16 h-16 rounded-2xl bg-indigo-100 flex items-center justify-center mb-5">
              <User size={28} className="text-indigo-500" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">Save your prompts</h2>
            <p className="text-gray-500 text-sm max-w-xs mb-6">
              Sign up after your first session to save and access all your prompts here.
            </p>
            <button
              onClick={() => navigate('/intake')}
              className="px-6 py-3 rounded-xl text-white font-semibold text-sm transition-all hover:opacity-90 active:scale-95"
              style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}
            >
              Start a vibe session →
            </button>
          </div>
        )}

        {/* Logged in, no history */}
        {user && history.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-5">
              <Zap size={28} className="text-gray-400" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">No prompts yet</h2>
            <p className="text-gray-500 text-sm max-w-xs mb-6">
              Start your first vibe session to generate and save prompts here.
            </p>
            <button
              onClick={() => navigate('/intake')}
              className="px-6 py-3 rounded-xl text-white font-semibold text-sm transition-all hover:opacity-90 active:scale-95"
              style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}
            >
              Start a vibe session →
            </button>
          </div>
        )}

        {/* History grid */}
        {user && history.length > 0 && (
          <>
            <p className="text-xs font-semibold uppercase tracking-widest text-gray-400 mb-5">
              {history.length} {history.length === 1 ? 'prompt' : 'prompts'} saved
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {history.map((entry) => (
                <div
                  key={entry.sessionId}
                  className="bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-md transition-shadow flex flex-col gap-3"
                >
                  {/* App name */}
                  <div>
                    <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-2">
                      {entry.appName || `Session ${entry.sessionId.slice(0, 8)}`}
                    </h3>
                  </div>

                  {/* Meta row */}
                  <div className="flex items-center gap-2 flex-wrap">
                    <PlatformBadge platform={entry.platform} />
                    <span className="flex items-center gap-1 text-xs text-gray-400">
                      <Clock size={11} />
                      {formatDate(entry.timestamp)}
                    </span>
                    <span className="flex items-center gap-1 text-xs text-gray-400 ml-auto">
                      <Zap size={11} />
                      {formatTokens(entry.tokenEstimate)} tokens
                    </span>
                  </div>

                  {/* Prompt preview */}
                  <p className="text-xs text-gray-400 line-clamp-2 font-mono leading-relaxed bg-gray-50 rounded-lg px-3 py-2">
                    {entry.prompt.slice(0, 120)}…
                  </p>

                  {/* Action */}
                  <button
                    onClick={() => setActiveEntry(entry)}
                    className="mt-auto flex items-center justify-center gap-1.5 w-full py-2 rounded-lg border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
                  >
                    <Eye size={13} />
                    View Prompt
                  </button>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Prompt modal */}
      {activeEntry && (
        <PromptModal entry={activeEntry} onClose={() => setActiveEntry(null)} />
      )}
    </div>
  )
}
