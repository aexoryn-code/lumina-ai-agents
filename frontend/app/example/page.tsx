'use client'

import { useState } from 'react'
import ChatInterface from '@/components/ChatInterface'
import AgentSelector from '@/components/AgentSelector'

export default function ExamplePage() {
  const [selectedAgent, setSelectedAgent] = useState<string>('commander')
  const [showChat, setShowChat] = useState(false)

  const handleSelectAgent = (agentId: string) => {
    setSelectedAgent(agentId)
    setShowChat(true)
  }

  return (
    <main className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
            Lumina AI Agents
          </h1>
          <p className="text-xl text-muted-foreground">
            Enterprise AI Operating System
          </p>
        </div>

        {/* Agent Selector */}
        {!showChat && (
          <div className="mb-8">
            <AgentSelector
              onSelectAgent={handleSelectAgent}
              selectedAgent={selectedAgent}
            />
            <div className="text-center mt-6">
              <button
                onClick={() => setShowChat(true)}
                disabled={!selectedAgent}
                className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Start Chat with {selectedAgent ? selectedAgent.charAt(0).toUpperCase() + selectedAgent.slice(1) : 'Agent'}
              </button>
            </div>
          </div>
        )}

        {/* Chat Interface */}
        {showChat && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <button
                onClick={() => setShowChat(false)}
                className="px-4 py-2 text-sm border border-border rounded-lg hover:bg-accent transition-colors"
              >
                ← Change Agent
              </button>
              <div className="text-sm text-muted-foreground">
                Chatting with: <span className="font-semibold">{selectedAgent}</span>
              </div>
            </div>

            <ChatInterface
              sessionId="example-session"
              agentType={selectedAgent as any}
            />
          </div>
        )}

        {/* Features */}
        {!showChat && (
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 border border-border rounded-lg bg-card">
              <h3 className="text-lg font-semibold mb-2">Multi-Agent System</h3>
              <p className="text-sm text-muted-foreground">
                5 specialized agents for different tasks: Commander, Coding, Research, Security, and UI/UX
              </p>
            </div>
            <div className="p-6 border border-border rounded-lg bg-card">
              <h3 className="text-lg font-semibold mb-2">Multi-Model Support</h3>
              <p className="text-sm text-muted-foreground">
                Intelligent routing across OpenAI, Claude, Gemini, DeepSeek, Mistral, and Groq
              </p>
            </div>
            <div className="p-6 border border-border rounded-lg bg-card">
              <h3 className="text-lg font-semibold mb-2">Memory Systems</h3>
              <p className="text-sm text-muted-foreground">
                Short-term, long-term, semantic, and episodic memory for context-aware conversations
              </p>
            </div>
          </div>
        )}
      </div>
    </main>
  )
}
