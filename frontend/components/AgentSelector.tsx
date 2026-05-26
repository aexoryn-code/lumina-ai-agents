'use client'

import { useState } from 'react'
import { Bot, Code, Search, Shield, Palette, ChevronRight } from 'lucide-react'

interface Agent {
  id: string
  name: string
  description: string
  icon: React.ReactNode
  color: string
}

const agents: Agent[] = [
  {
    id: 'commander',
    name: 'Commander Agent',
    description: 'Master orchestrator that coordinates multiple agents for complex tasks',
    icon: <Bot className="w-6 h-6" />,
    color: 'from-blue-500 to-cyan-500',
  },
  {
    id: 'coding',
    name: 'Coding Agent',
    description: 'Expert in software development, debugging, and code optimization',
    icon: <Code className="w-6 h-6" />,
    color: 'from-green-500 to-emerald-500',
  },
  {
    id: 'research',
    name: 'Research Agent',
    description: 'Specialized in information retrieval, analysis, and synthesis',
    icon: <Search className="w-6 h-6" />,
    color: 'from-purple-500 to-pink-500',
  },
  {
    id: 'security',
    name: 'Security Agent',
    description: 'Expert in security analysis, vulnerability detection, and threat assessment',
    icon: <Shield className="w-6 h-6" />,
    color: 'from-red-500 to-orange-500',
  },
  {
    id: 'uiux',
    name: 'UI/UX Agent',
    description: 'Specialized in interface design, user experience, and visual systems',
    icon: <Palette className="w-6 h-6" />,
    color: 'from-yellow-500 to-amber-500',
  },
]

interface AgentSelectorProps {
  onSelectAgent: (agentId: string) => void
  selectedAgent?: string
}

export default function AgentSelector({
  onSelectAgent,
  selectedAgent,
}: AgentSelectorProps) {
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null)

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold mb-2">Select an AI Agent</h2>
        <p className="text-muted-foreground">
          Choose a specialized agent for your task
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents.map((agent) => (
          <button
            key={agent.id}
            onClick={() => onSelectAgent(agent.id)}
            onMouseEnter={() => setHoveredAgent(agent.id)}
            onMouseLeave={() => setHoveredAgent(null)}
            className={`
              relative p-6 rounded-xl border-2 transition-all duration-300
              ${
                selectedAgent === agent.id
                  ? 'border-primary bg-primary/5 scale-105'
                  : 'border-border hover:border-primary/50 hover:scale-105'
              }
              ${hoveredAgent === agent.id ? 'shadow-lg' : 'shadow'}
            `}
          >
            {/* Icon with gradient background */}
            <div
              className={`
                w-12 h-12 rounded-lg bg-gradient-to-br ${agent.color}
                flex items-center justify-center text-white mb-4
                transition-transform duration-300
                ${hoveredAgent === agent.id ? 'scale-110' : 'scale-100'}
              `}
            >
              {agent.icon}
            </div>

            {/* Agent name */}
            <h3 className="text-lg font-semibold mb-2 text-left">
              {agent.name}
            </h3>

            {/* Description */}
            <p className="text-sm text-muted-foreground text-left mb-4">
              {agent.description}
            </p>

            {/* Select indicator */}
            <div className="flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                {selectedAgent === agent.id ? 'Selected' : 'Click to select'}
              </span>
              <ChevronRight
                className={`
                  w-4 h-4 transition-transform duration-300
                  ${hoveredAgent === agent.id ? 'translate-x-1' : 'translate-x-0'}
                `}
              />
            </div>

            {/* Selected indicator */}
            {selectedAgent === agent.id && (
              <div className="absolute top-2 right-2">
                <div className="w-3 h-3 rounded-full bg-primary animate-pulse" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Selected agent info */}
      {selectedAgent && (
        <div className="mt-8 p-6 rounded-lg bg-card border border-border">
          <div className="flex items-center gap-3 mb-3">
            <div
              className={`
                w-10 h-10 rounded-lg bg-gradient-to-br
                ${agents.find((a) => a.id === selectedAgent)?.color}
                flex items-center justify-center text-white
              `}
            >
              {agents.find((a) => a.id === selectedAgent)?.icon}
            </div>
            <div>
              <h4 className="font-semibold">
                {agents.find((a) => a.id === selectedAgent)?.name}
              </h4>
              <p className="text-sm text-muted-foreground">Ready to assist</p>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            {agents.find((a) => a.id === selectedAgent)?.description}
          </p>
        </div>
      )}
    </div>
  )
}
