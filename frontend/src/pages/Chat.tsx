import { useState, useRef, useEffect } from 'react'
import { sendMessage } from '../api/chat'

const SESSION_KEY = 'wiki_chat_session_id'

type Message = {
  role: 'user' | 'assistant'
  content: string
  sources?: string[]
}

interface ChatProps {
  onNavigateToWiki: (slug: string) => void
}

export function Chat({ onNavigateToWiki }: ChatProps) {
  const [sessionId] = useState<string>(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) return stored
    const id = crypto.randomUUID()
    localStorage.setItem(SESSION_KEY, id)
    return id
  })

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Ciao! Posso rispondere a domande sulle procedure aziendali. Cosa vuoi sapere?',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      const data = await sendMessage(text, sessionId)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.answer, sources: data.sources },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Errore di connessione. Riprova.' },
      ])
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-72px)]">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 max-w-3xl mx-auto w-full">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-nav text-white'
                  : 'bg-white border border-gray-200 text-gray-800'
              }`}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {msg.sources.map((slug) => (
                    <button
                      key={slug}
                      onClick={() => onNavigateToWiki(slug)}
                      className="text-xs bg-accent/10 text-accent border border-accent/30 px-2 py-0.5 rounded hover:bg-accent hover:text-white transition-colors font-mono"
                    >
                      {slug}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:150ms]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:300ms]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-200 bg-white px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Scrivi una domanda sulle procedure aziendali..."
            rows={1}
            className="flex-1 resize-none border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-accent disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-5 py-2 bg-nav text-white text-sm font-mono hover:bg-accent transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            style={{ borderRadius: '2px' }}
          >
            Invia
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-2 font-mono">
          Invio per inviare · Shift+Invio per andare a capo
        </p>
      </div>
    </div>
  )
}
