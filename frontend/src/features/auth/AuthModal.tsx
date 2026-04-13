import { useState, useEffect } from 'react'
import { X, Sparkles, User, Mail } from 'lucide-react'
import { getUser, saveUser } from '../../lib/auth'
import { useSessionStore } from '../../lib/store'

interface AuthModalProps {
  onContinue: () => void
  onSkip: () => void
}

export default function AuthModal({ onContinue, onSkip }: AuthModalProps) {
  const { setUser } = useSessionStore()
  const existingUser = getUser()

  const [email, setEmail] = useState('')
  const [name, setName] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  // If already logged in, auto-proceed after 1.5s
  useEffect(() => {
    if (existingUser) {
      const timer = setTimeout(() => {
        onContinue()
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [existingUser, onContinue])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!email.trim()) {
      setError('Please enter your email.')
      return
    }
    if (!name.trim()) {
      setError('Please enter your name.')
      return
    }

    setSubmitting(true)
    const user = { email: email.trim(), name: name.trim(), createdAt: new Date().toISOString() }
    saveUser(user)
    setUser(user)
    setSubmitting(false)
    onContinue()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onSkip}
      />

      {/* Card */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-in fade-in zoom-in-95 duration-200">
        {/* Close button */}
        <button
          onClick={onSkip}
          className="absolute top-4 right-4 p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
        >
          <X size={16} />
        </button>

        {existingUser ? (
          // Returning user state
          <div className="text-center py-4">
            <div className="w-14 h-14 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-4">
              <User size={24} className="text-indigo-600" />
            </div>
            <h2 className="text-xl font-bold text-gray-900 mb-2">
              Welcome back, {existingUser.name}!
            </h2>
            <p className="text-gray-500 text-sm">
              Your prompt is being saved to your account.
            </p>
            <div className="mt-6 flex justify-center gap-1">
              <span className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce" style={{ animationDelay: '150ms' }} />
              <span className="w-2 h-2 rounded-full bg-indigo-300 animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        ) : (
          // Sign up state
          <>
            <div className="flex items-center gap-3 mb-6">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}
              >
                <Sparkles size={18} className="text-white" />
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Your prompt is ready 🎉</h2>
              </div>
            </div>

            <p className="text-gray-500 text-sm mb-6 leading-relaxed">
              Sign up to save your prompt and access it later from any device.
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase tracking-wide">
                  Your Name
                </label>
                <div className="relative">
                  <User size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Jane Smith"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                    autoFocus
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 mb-1.5 uppercase tracking-wide">
                  Email Address
                </label>
                <div className="relative">
                  <Mail size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                  <input
                    type="email"
                    placeholder="jane@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-9 pr-3 py-2.5 rounded-lg border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                  />
                </div>
              </div>

              {error && (
                <p className="text-red-500 text-xs">{error}</p>
              )}

              <button
                type="submit"
                disabled={submitting}
                className="w-full py-3 rounded-xl text-white font-semibold text-sm transition-all hover:opacity-90 active:scale-95 disabled:opacity-50 mt-2"
                style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}
              >
                {submitting ? 'Saving...' : 'Save My Prompt →'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={onSkip}
                className="text-xs text-gray-400 hover:text-gray-600 transition-colors underline underline-offset-2"
              >
                Skip for now
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
