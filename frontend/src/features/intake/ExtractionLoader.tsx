export default function ExtractionLoader() {
  return (
    <div className="fixed inset-0 bg-white/90 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="text-center space-y-4">
        <div className="w-12 h-12 border-4 border-blue-200 border-t-blue-500 rounded-full animate-spin mx-auto" />
        <div>
          <p className="font-semibold text-gray-900">Analysing your idea...</p>
          <p className="text-sm text-gray-500 mt-1">Extracting product context with AI</p>
        </div>
        <div className="flex justify-center gap-1 pt-2">
          {['Parsing requirements', 'Mapping features', 'Scoring complexity'].map((step, i) => (
            <span
              key={step}
              className="text-xs text-gray-400 bg-gray-100 rounded-full px-2 py-0.5"
              style={{ animationDelay: `${i * 0.3}s` }}
            >
              {step}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
