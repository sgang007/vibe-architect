export interface User {
  email: string
  name: string
  createdAt: string
}

export interface HistoryEntry {
  sessionId: string
  appName: string
  platform: string
  prompt: string
  tokenEstimate: number
  timestamp: string
}

const USER_KEY = 'vibe_architect_user'
const HISTORY_KEY = 'vibe_architect_history'

export function getUser(): User | null {
  try {
    const raw = localStorage.getItem(USER_KEY)
    if (!raw) return null
    return JSON.parse(raw) as User
  } catch {
    return null
  }
}

export function saveUser(user: User): void {
  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function logout(): void {
  localStorage.removeItem(USER_KEY)
}

export function getHistory(): HistoryEntry[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY)
    if (!raw) return []
    return JSON.parse(raw) as HistoryEntry[]
  } catch {
    return []
  }
}

export function saveHistoryEntry(entry: HistoryEntry): void {
  const history = getHistory()
  // Prepend the new entry so newest is first
  const updated = [entry, ...history.filter((h) => h.sessionId !== entry.sessionId)]
  localStorage.setItem(HISTORY_KEY, JSON.stringify(updated))
}
