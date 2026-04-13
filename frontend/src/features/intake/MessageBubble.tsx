import type { Message } from '../../lib/store'

export default function MessageBubble({ message }: { message: Message }) {
  const isUser = message.type === 'answer'
  const isSystem = message.type === 'system'

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <span className="text-xs text-gray-400 bg-gray-100 rounded-full px-3 py-1">
          {message.text}
        </span>
      </div>
    )
  }

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} fade-in`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm ${
          isUser
            ? 'bg-blue-500 text-white rounded-br-sm'
            : message.type === 'probe'
            ? 'bg-amber-50 border border-amber-200 text-amber-900 rounded-bl-sm'
            : 'bg-white border border-gray-200 text-gray-900 rounded-bl-sm shadow-sm'
        }`}
      >
        {message.type === 'probe' && (
          <p className="text-xs font-medium text-amber-600 mb-1">Follow-up question</p>
        )}
        <p className="leading-relaxed">{message.text}</p>
      </div>
    </div>
  )
}
