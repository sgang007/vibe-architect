import { Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './features/landing/LandingPage'
import IntakePage from './features/intake/IntakePage'
import PreviewPage from './features/preview/PreviewPage'
import CompilerPage from './features/compiler/CompilerPage'
import HistoryPage from './features/history/HistoryPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/intake" element={<IntakePage />} />
      <Route path="/preview/:sessionId" element={<PreviewPage />} />
      <Route path="/compile/:sessionId" element={<CompilerPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
