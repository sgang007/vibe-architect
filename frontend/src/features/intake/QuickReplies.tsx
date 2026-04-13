export default function QuickReplies({
  options,
  onSelect,
}: {
  options: string[]
  onSelect: (v: string) => void
}) {
  return (
    <div className="flex flex-wrap gap-2 pb-3">
      {options.map((opt) => (
        <button
          key={opt}
          onClick={() => onSelect(opt)}
          className="text-xs bg-white border border-blue-200 text-blue-600 rounded-full px-3 py-1.5 hover:bg-blue-50 transition-colors"
        >
          {opt}
        </button>
      ))}
    </div>
  )
}
