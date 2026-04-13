import { useState, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { compilePrompt } from '../../lib/api'
import { saveHistoryEntry, getUser } from '../../lib/auth'
import { ArrowLeft, Copy, Download, ExternalLink, Check, Loader2, History } from 'lucide-react'

type Platform = 'replit' | 'bolt' | 'lovable' | 'v0' | 'cursor' | 'emergent'

interface PlatformConfig {
  id: Platform
  label: string
  color: string
  activeColor: string
  url: string
  description: string
}

const PLATFORMS: PlatformConfig[] = [
  {
    id: 'replit',
    label: 'Replit',
    color: 'bg-orange-50 border-orange-200 text-orange-700',
    activeColor: 'bg-orange-500 border-orange-500 text-white',
    url: 'https://replit.com',
    description: 'Full-stack in browser',
  },
  {
    id: 'bolt',
    label: 'Bolt',
    color: 'bg-purple-50 border-purple-200 text-purple-700',
    activeColor: 'bg-purple-600 border-purple-600 text-white',
    url: 'https://bolt.new',
    description: 'Instant full-stack apps',
  },
  {
    id: 'lovable',
    label: 'Lovable',
    color: 'bg-pink-50 border-pink-200 text-pink-700',
    activeColor: 'bg-pink-500 border-pink-500 text-white',
    url: 'https://lovable.dev',
    description: 'React apps in minutes',
  },
  {
    id: 'v0',
    label: 'v0',
    color: 'bg-gray-50 border-gray-300 text-gray-700',
    activeColor: 'bg-gray-900 border-gray-900 text-white',
    url: 'https://v0.dev',
    description: 'UI generation by Vercel',
  },
  {
    id: 'cursor',
    label: 'Cursor',
    color: 'bg-blue-50 border-blue-200 text-blue-700',
    activeColor: 'bg-blue-600 border-blue-600 text-white',
    url: 'https://cursor.sh',
    description: 'AI-native code editor',
  },
  {
    id: 'emergent',
    label: 'Emergent',
    color: 'bg-teal-50 border-teal-200 text-teal-700',
    activeColor: 'bg-teal-600 border-teal-600 text-white',
    url: 'https://emergent.sh',
    description: 'AI agent builder',
  },
]

function TokenBadge({ estimate }: { estimate: number }) {
  const k = (estimate / 1000).toFixed(1)
  const color =
    estimate < 4000
      ? 'bg-green-50 text-green-700 border-green-200'
      : estimate < 8000
      ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
      : 'bg-red-50 text-red-700 border-red-200'
  return (
    <span className={`text-xs font-medium border rounded-full px-2.5 py-0.5 ${color}`}>
      ~{k}k tokens
    </span>
  )
}

export default function CompilerPage() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const [selectedPlatform, setSelectedPlatform] = useState<Platform | null>(null)
  const [compiledData, setCompiledData] = useState<{
    prompt: string
    token_estimate: number
  } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [downloaded, setDownloaded] = useState(false)

  const handlePlatformSelect = useCallback(
    async (platform: Platform) => {
      if (!sessionId) return
      setSelectedPlatform(platform)
      setIsLoading(true)
      setError(null)
      setCompiledData(null)
      try {
        const result = await compilePrompt(sessionId, platform)
        setCompiledData(result)
        // Save to history if user is logged in
        const user = getUser()
        if (user && result.prompt) {
          saveHistoryEntry({
            sessionId,
            appName: `App · ${new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`,
            platform,
            prompt: result.prompt,
            tokenEstimate: result.token_estimate,
            timestamp: new Date().toISOString(),
          })
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Compilation failed')
      } finally {
        setIsLoading(false)
      }
    },
    [sessionId],
  )

  const handleCopy = useCallback(async () => {
    if (!compiledData?.prompt) return
    try {
      await navigator.clipboard.writeText(compiledData.prompt)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback
      const el = document.createElement('textarea')
      el.value = compiledData.prompt
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }, [compiledData])

  const handleDownload = useCallback(() => {
    if (!compiledData?.prompt || !sessionId) return
    const blob = new Blob([compiledData.prompt], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${sessionId}-prompt.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setDownloaded(true)
    setTimeout(() => setDownloaded(false), 2000)
  }, [compiledData, sessionId])

  const handleOpenPlatform = useCallback(() => {
    const platform = PLATFORMS.find((p) => p.id === selectedPlatform)
    if (platform) {
      window.open(platform.url, '_blank', 'noopener,noreferrer')
    }
  }, [selectedPlatform])

  const currentPlatformConfig = PLATFORMS.find((p) => p.id === selectedPlatform)

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
          <h1 className="font-semibold text-gray-900 text-sm">Build Prompt</h1>
          <p className="text-xs text-gray-500">Select a platform to compile</p>
        </div>
        {compiledData && <TokenBadge estimate={compiledData.token_estimate} />}
        {getUser() && (
          <button
            onClick={() => navigate('/history')}
            className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors ml-1"
            title="View prompt history"
          >
            <History size={16} className="text-gray-500" />
          </button>
        )}
      </header>

      {/* Platform Selector */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="max-w-2xl mx-auto">
          <p className="text-xs text-gray-500 font-medium mb-3 uppercase tracking-wide">
            Choose Platform
          </p>
          <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                onClick={() => handlePlatformSelect(p.id)}
                disabled={isLoading}
                className={`flex flex-col items-center gap-1 rounded-xl border px-2 py-3 text-xs font-medium transition-all disabled:opacity-60 ${
                  selectedPlatform === p.id ? p.activeColor : p.color + ' hover:opacity-80'
                }`}
              >
                <span className="font-bold text-sm">{p.label}</span>
                <span
                  className={`text-center leading-tight ${
                    selectedPlatform === p.id ? 'opacity-80' : 'opacity-60'
                  }`}
                  style={{ fontSize: '10px' }}
                >
                  {p.description}
                </span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-6 max-w-2xl mx-auto w-full">
        {!selectedPlatform && (
          <div className="text-center py-20 text-gray-400">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">🏗️</span>
            </div>
            <p className="font-medium text-gray-600">Select a platform above</p>
            <p className="text-sm mt-1">We'll compile your prompt for that environment</p>
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <Loader2 size={32} className="animate-spin text-blue-500" />
            <div className="text-center">
              <p className="font-medium text-gray-700">
                Compiling for {currentPlatformConfig?.label}...
              </p>
              <p className="text-sm text-gray-400 mt-1">Optimising prompt for platform</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
            <p className="text-red-700 font-medium text-sm">Compilation failed</p>
            <p className="text-red-500 text-xs mt-1">{error}</p>
            <button
              onClick={() => selectedPlatform && handlePlatformSelect(selectedPlatform)}
              className="mt-3 text-sm text-red-600 underline"
            >
              Retry
            </button>
          </div>
        )}

        {compiledData && !isLoading && (
          <div className="space-y-4 fade-in">
            {/* Action buttons */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleCopy}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                  copied
                    ? 'bg-green-50 border-green-300 text-green-700'
                    : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? 'Copied!' : 'Copy All'}
              </button>
              <button
                onClick={handleDownload}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg border text-sm font-medium transition-all ${
                  downloaded
                    ? 'bg-green-50 border-green-300 text-green-700'
                    : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50'
                }`}
              >
                {downloaded ? <Check size={14} /> : <Download size={14} />}
                {downloaded ? 'Downloaded!' : 'Export .md'}
              </button>
              {currentPlatformConfig && (
                <button
                  onClick={handleOpenPlatform}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg border bg-blue-500 border-blue-500 text-white text-sm font-medium hover:bg-blue-600 transition-colors ml-auto"
                >
                  <ExternalLink size={14} />
                  Open {currentPlatformConfig.label}
                </button>
              )}
            </div>

            {/* Token info */}
            <div className="flex items-center justify-between bg-white rounded-lg border border-gray-200 px-4 py-3">
              <div>
                <p className="text-xs text-gray-500">Token Estimate</p>
                <p className="text-sm font-semibold text-gray-900">
                  {compiledData.token_estimate.toLocaleString()} tokens
                </p>
              </div>
              <TokenBadge estimate={compiledData.token_estimate} />
            </div>

            {/* Prompt output */}
            <div className="bg-gray-900 rounded-xl overflow-hidden shadow-sm">
              <div className="flex items-center justify-between px-4 py-2.5 bg-gray-800 border-b border-gray-700">
                <span className="text-xs text-gray-400 font-mono">
                  {sessionId}-prompt.md
                </span>
                <button
                  onClick={handleCopy}
                  className="text-xs text-gray-400 hover:text-gray-200 transition-colors flex items-center gap-1"
                >
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copied' : 'Copy'}
                </button>
              </div>
              <pre className="text-xs text-gray-200 font-mono p-4 overflow-x-auto overflow-y-auto max-h-[500px] leading-relaxed whitespace-pre-wrap break-words">
                {compiledData.prompt}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* Bottom action */}
      {compiledData && !isLoading && currentPlatformConfig && (
        <div className="bg-white border-t border-gray-200 px-4 py-4">
          <div className="max-w-2xl mx-auto flex gap-2">
            <button
              onClick={handleCopy}
              className="flex-1 flex items-center justify-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium rounded-lg px-4 py-3 transition-colors text-sm"
            >
              <Copy size={15} />
              Copy Prompt
            </button>
            <button
              onClick={handleOpenPlatform}
              className="flex-1 flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg px-4 py-3 transition-colors text-sm"
            >
              <ExternalLink size={15} />
              Open {currentPlatformConfig.label}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
