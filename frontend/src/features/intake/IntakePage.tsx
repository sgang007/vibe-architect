import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { createSession, submitAnswerSSE } from '../../lib/api'
import { useSessionStore } from '../../lib/store'
import MessageBubble from './MessageBubble'
import QuickReplies from './QuickReplies'
import PhaseProgressBar from './PhaseProgressBar'
import ExtractionLoader from './ExtractionLoader'
import AuthModal from '../auth/AuthModal'
import { Send } from 'lucide-react'

let msgId = 0
const newId = () => String(++msgId)

export default function IntakePage() {
  const navigate = useNavigate()
  const [input, setInput] = useState('')
  const [quickReplies, setQuickReplies] = useState<string[]>([])
  const [submitting, setSubmitting] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const initialized = useRef(false)

  const {
    sessionId,
    phase,
    messages,
    progressPct,
    showAuthModal,
    setSessionId,
    setPhase,
    addMessage,
    setProgress,
    setLoading,
    setComplexity,
    setShowAuthModal,
  } = useSessionStore()

  useEffect(() => {
    if (!sessionId && !initialized.current) {
      initialized.current = true
      createSession()
        .then((data) => {
          setSessionId(data.session_id)
          setPhase(data.phase as Parameters<typeof setPhase>[0])
          addMessage({
            id: newId(),
            type: 'question',
            text: data.first_question,
            quickReplies: data.quick_replies,
            timestamp: Date.now(),
          })
          setQuickReplies(data.quick_replies)
        })
        .catch(() => {
          addMessage({
            id: newId(),
            type: 'system',
            text: 'Failed to connect to backend. Please ensure the API server is running.',
            timestamp: Date.now(),
          })
        })
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (text: string) => {
    if (!text.trim() || !sessionId || submitting) return
    const userText = text.trim()
    setInput('')
    setQuickReplies([])
    setSubmitting(true)

    addMessage({ id: newId(), type: 'answer', text: userText, timestamp: Date.now() })

    try {
      await submitAnswerSSE(sessionId, userText, (event, data: unknown) => {
        const d = data as Record<string, unknown>
        if (event === 'question') {
          addMessage({
            id: newId(),
            type: 'question',
            text: d.text as string,
            quickReplies: (d.quick_replies as string[]) || [],
            timestamp: Date.now(),
          })
          setQuickReplies((d.quick_replies as string[]) || [])
          if (d.progress_pct) setProgress(d.progress_pct as number)
          if (d.phase) setPhase(d.phase as Parameters<typeof setPhase>[0])
        } else if (event === 'probe') {
          addMessage({ id: newId(), type: 'probe', text: d.text as string, timestamp: Date.now() })
        } else if (event === 'phase_advance') {
          setPhase(d.new_phase as Parameters<typeof setPhase>[0])
          if (d.progress_pct) setProgress(d.progress_pct as number)
          addMessage({
            id: newId(),
            type: 'system',
            text: `Moving to: ${(d.label as string) || (d.new_phase as string)}`,
            timestamp: Date.now(),
          })
        } else if (event === 'extracting') {
          setPhase('EXTRACTING')
          setLoading(true)
        } else if (event === 'extracted') {
          setPhase('ENRICHED')
          setLoading(false)
          setProgress(100)
          if (d.complexity_score) setComplexity(d.complexity_score as number)
          // Show auth modal after extraction completes
          setShowAuthModal(true)
        } else if (event === 'error') {
          setLoading(false)
          const msg = d.message as string
          const isRateLimit = msg?.toLowerCase().includes('rate limit') || msg?.toLowerCase().includes('quota')
          addMessage({
            id: newId(),
            type: 'system',
            text: isRateLimit
              ? '⚠️ The AI is temporarily rate-limited (free tier). Please wait a minute and try again, or refresh the page.'
              : `Error: ${msg}`,
            timestamp: Date.now(),
          })
        }
      })
    } catch (err) {
      addMessage({
        id: newId(),
        type: 'system',
        text: `Connection error: ${err instanceof Error ? err.message : 'Unknown error'}`,
        timestamp: Date.now(),
      })
    } finally {
      setSubmitting(false)
    }
  }

  const isExtracting = phase === 'EXTRACTING'
  const isEnriched = phase === 'ENRICHED' || phase === 'PREVIEWING' || phase === 'READY'

  const handleAuthContinue = () => {
    setShowAuthModal(false)
    navigate(`/preview/${sessionId}`)
  }

  const handleAuthSkip = () => {
    setShowAuthModal(false)
    navigate(`/preview/${sessionId}`)
  }

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3 sticky top-0 z-10">
        <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-sm">VA</span>
        </div>
        <div>
          <h1 className="font-semibold text-gray-900 text-sm">Vibe Architect</h1>
          <p className="text-xs text-gray-500">AI Prompt Builder</p>
        </div>
      </header>

      <PhaseProgressBar phase={phase} progressPct={progressPct} />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full space-y-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-32">
            <div className="flex gap-1">
              <div
                className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce"
                style={{ animationDelay: '0ms' }}
              />
              <div
                className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce"
                style={{ animationDelay: '150ms' }}
              />
              <div
                className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce"
                style={{ animationDelay: '300ms' }}
              />
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        {submitting && (
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <div className="flex gap-1">
              <div
                className="w-2 h-2 rounded-full bg-gray-300 animate-bounce"
                style={{ animationDelay: '0ms' }}
              />
              <div
                className="w-2 h-2 rounded-full bg-gray-300 animate-bounce"
                style={{ animationDelay: '150ms' }}
              />
              <div
                className="w-2 h-2 rounded-full bg-gray-300 animate-bounce"
                style={{ animationDelay: '300ms' }}
              />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Quick Replies */}
      {quickReplies.length > 0 && !isEnriched && (
        <div className="px-4 max-w-2xl mx-auto w-full">
          <QuickReplies options={quickReplies} onSelect={(r) => handleSend(r)} />
        </div>
      )}

      {/* Input */}
      {!isEnriched && (
        <div className="bg-white border-t border-gray-200 px-4 py-3 max-w-2xl mx-auto w-full">
          <div className="flex gap-2">
            <input
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-gray-50"
              placeholder="Type your answer..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend(input)}
              disabled={submitting || isExtracting}
            />
            <button
              className="bg-indigo-500 hover:bg-indigo-600 text-white rounded-lg px-3 py-2 disabled:opacity-50 transition-colors"
              onClick={() => handleSend(input)}
              disabled={!input.trim() || submitting || isExtracting}
            >
              <Send size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Generate Preview CTA */}
      {isEnriched && !showAuthModal && (
        <div className="bg-white border-t border-gray-200 px-4 py-4 max-w-2xl mx-auto w-full">
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center gap-2 mb-3">
              <div className="w-6 h-6 rounded-full bg-green-100 flex items-center justify-center">
                <svg
                  className="w-3.5 h-3.5 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2.5}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm text-gray-600 font-medium">Your app idea has been analysed!</p>
            </div>
            <button
              className="w-full bg-indigo-500 hover:bg-indigo-600 text-white font-medium rounded-lg px-4 py-3 transition-colors"
              onClick={() => navigate(`/preview/${sessionId}`)}
            >
              Generate Preview →
            </button>
          </div>
        </div>
      )}

      {isExtracting && <ExtractionLoader />}

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal onContinue={handleAuthContinue} onSkip={handleAuthSkip} />
      )}
    </div>
  )
}
