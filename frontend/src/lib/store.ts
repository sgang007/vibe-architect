import { create } from 'zustand'
import type { User } from './auth'

export type Phase =
  | 'IDLE'
  | 'IDEA'
  | 'TOUCHPOINTS'
  | 'FEATURES'
  | 'TECHNICAL'
  | 'EXTRACTING'
  | 'ENRICHED'
  | 'PREVIEWING'
  | 'READY'

export interface Message {
  id: string
  type: 'question' | 'answer' | 'probe' | 'system'
  text: string
  quickReplies?: string[]
  timestamp: number
}

interface SessionState {
  sessionId: string | null
  phase: Phase
  messages: Message[]
  progressPct: number
  isLoading: boolean
  complexityScore: number | null
  user: User | null
  showAuthModal: boolean
  setSessionId: (id: string) => void
  setPhase: (phase: Phase) => void
  addMessage: (msg: Message) => void
  setProgress: (pct: number) => void
  setLoading: (loading: boolean) => void
  setComplexity: (score: number) => void
  setUser: (user: User | null) => void
  setShowAuthModal: (show: boolean) => void
  reset: () => void
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  phase: 'IDLE',
  messages: [],
  progressPct: 0,
  isLoading: false,
  complexityScore: null,
  user: null,
  showAuthModal: false,
  setSessionId: (id) => set({ sessionId: id }),
  setPhase: (phase) => set({ phase }),
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  setProgress: (progressPct) => set({ progressPct }),
  setLoading: (isLoading) => set({ isLoading }),
  setComplexity: (complexityScore) => set({ complexityScore }),
  setUser: (user) => set({ user }),
  setShowAuthModal: (showAuthModal) => set({ showAuthModal }),
  reset: () =>
    set({
      sessionId: null,
      phase: 'IDLE',
      messages: [],
      progressPct: 0,
      isLoading: false,
      complexityScore: null,
    }),
}))
