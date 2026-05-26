'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Wifi, WifiOff } from 'lucide-react'
import { useChatWebSocket } from '@/lib/useWebSocket'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

interface StreamingChatProps {
  sessionId?: string
  agentType?: 'commander' | 'coding' | 'research' | 'security' | 'uiux'
}

export default function StreamingChat({
  sessionId = 'default',
  agentType = 'commander'
}: StreamingChatProps) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const {
    sendChat,
    isConnected,
    isStreaming,
    currentStream,
    reconnect,
  } = useChatWebSocket(sessionId)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, currentStream])

  const handleSend = () => {
    if (!input.trim() || !isConnected) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    sendChat(input, agentType)
    setInput('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full max-h-[800px] border border-border rounded-lg bg-card">
      {/* Header with connection status */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">
            Streaming Chat - {agentType.charAt(0).toUpperCase() + agentType.slice(1)}
          </h2>
          <p className="text-sm text-muted-foreground">
            Real-time WebSocket communication
          </p>
        </div>
        <div className="flex items-center gap-2">
          {isConnected ? (
            <>
              <Wifi className="w-5 h-5 text-green-500" />
              <span className="text-sm text-green-500">Connected</span>
            </>
          ) : (
            <>
              <WifiOff className="w-5 h-5 text-red-500" />
              <span className="text-sm text-red-500">Disconnected</span>
              <button
                onClick={reconnect}
                className="ml-2 px-2 py-1 text-xs bg-primary text-primary-foreground rounded"
              >
                Reconnect
              </button>
            </>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && !isStreaming && (
          <div className="text-center text-muted-foreground py-12">
            <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Start a conversation with real-time streaming</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                <Bot className="w-5 h-5 text-primary-foreground" />
              </div>
            )}

            <div
              className={`max-w-[70%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap break-words">
                {message.content}
              </p>
              <p className="text-xs opacity-70 mt-1">
                {message.timestamp.toLocaleTimeString()}
              </p>
            </div>

            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0">
                <User className="w-5 h-5 text-secondary-foreground" />
              </div>
            )}
          </div>
        ))}

        {/* Streaming message */}
        {isStreaming && currentStream && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="max-w-[70%] rounded-lg p-3 bg-muted">
              <p className="text-sm whitespace-pre-wrap break-words">
                {currentStream}
                <span className="inline-block w-2 h-4 ml-1 bg-foreground animate-pulse" />
              </p>
            </div>
          </div>
        )}

        {/* Loading indicator */}
        {isStreaming && !currentStream && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="bg-muted rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isConnected
                ? 'Type your message...'
                : 'Connecting to WebSocket...'
            }
            className="flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            rows={1}
            disabled={!isConnected || isStreaming}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || !isConnected || isStreaming}
            className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          {isStreaming
            ? 'Streaming response...'
            : isConnected
            ? 'Press Enter to send'
            : 'Waiting for connection...'}
        </p>
      </div>
    </div>
  )
}
