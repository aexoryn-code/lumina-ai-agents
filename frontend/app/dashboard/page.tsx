'use client'

import { motion } from 'framer-motion'
import { Bot, Zap, Activity, TrendingUp, Clock, Cpu } from 'lucide-react'
import { useAgentStatusWebSocket } from '@/lib/useWebSocket'
import { useEffect, useState } from 'react'

interface AgentStats {
  status: string
  executions: number
}

export default function DashboardPage() {
  const { agentStatus, isConnected } = useAgentStatusWebSocket()
  const [totalExecutions, setTotalExecutions] = useState(0)
  const [activeAgents, setActiveAgents] = useState(0)

  useEffect(() => {
    if (agentStatus) {
      const total = Object.values(agentStatus).reduce(
        (sum: number, agent: any) => sum + (agent.executions || 0),
        0
      )
      setTotalExecutions(total)

      const active = Object.values(agentStatus).filter(
        (agent: any) => agent.status === 'executing'
      ).length
      setActiveAgents(active)
    }
  }, [agentStatus])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-950 p-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
          Lumina AI Dashboard
        </h1>
        <p className="text-slate-400">Real-time agent monitoring and analytics</p>
      </motion.div>

      {/* Connection Status */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mb-6 flex items-center gap-2"
      >
        <div
          className={`w-2 h-2 rounded-full ${
            isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`}
        />
        <span className="text-sm text-slate-400">
          {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={<Bot className="w-6 h-6" />}
          label="Total Agents"
          value={Object.keys(agentStatus).length}
          color="from-blue-500 to-cyan-500"
          delay={0.1}
        />
        <StatCard
          icon={<Activity className="w-6 h-6" />}
          label="Active Now"
          value={activeAgents}
          color="from-green-500 to-emerald-500"
          delay={0.2}
        />
        <StatCard
          icon={<Zap className="w-6 h-6" />}
          label="Total Executions"
          value={totalExecutions}
          color="from-purple-500 to-pink-500"
          delay={0.3}
        />
        <StatCard
          icon={<TrendingUp className="w-6 h-6" />}
          label="Success Rate"
          value="98.5%"
          color="from-orange-500 to-red-500"
          delay={0.4}
        />
      </div>

      {/* Agent Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Agent Status Cards */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glassmorphism rounded-2xl p-6"
        >
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Cpu className="w-5 h-5 text-blue-400" />
            Agent Status
          </h2>
          <div className="space-y-3">
            {Object.entries(agentStatus).map(([id, agent]: [string, any], index) => (
              <AgentStatusCard
                key={id}
                id={id}
                status={agent.status}
                executions={agent.executions}
                delay={0.6 + index * 0.1}
              />
            ))}
          </div>
        </motion.div>

        {/* Activity Feed */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glassmorphism rounded-2xl p-6"
        >
          <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-purple-400" />
            Recent Activity
          </h2>
          <div className="space-y-3">
            <ActivityItem
              agent="Commander"
              action="Orchestrated multi-agent task"
              time="2 min ago"
              delay={0.7}
            />
            <ActivityItem
              agent="Coding"
              action="Generated Python function"
              time="5 min ago"
              delay={0.8}
            />
            <ActivityItem
              agent="Security"
              action="Completed security audit"
              time="8 min ago"
              delay={0.9}
            />
            <ActivityItem
              agent="Research"
              action="Analyzed documentation"
              time="12 min ago"
              delay={1.0}
            />
          </div>
        </motion.div>
      </div>

      {/* Performance Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.1 }}
        className="glassmorphism rounded-2xl p-6"
      >
        <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <MetricCard
            label="Avg Response Time"
            value="1.2s"
            trend="-15%"
            positive={true}
          />
          <MetricCard
            label="Token Usage"
            value="45.2K"
            trend="+8%"
            positive={false}
          />
          <MetricCard
            label="Cache Hit Rate"
            value="87%"
            trend="+12%"
            positive={true}
          />
        </div>
      </motion.div>
    </div>
  )
}

function StatCard({
  icon,
  label,
  value,
  color,
  delay,
}: {
  icon: React.ReactNode
  label: string
  value: number | string
  color: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="glassmorphism rounded-2xl p-6 hover:scale-105 transition-transform"
    >
      <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${color} flex items-center justify-center mb-4`}>
        {icon}
      </div>
      <p className="text-sm text-slate-400 mb-1">{label}</p>
      <p className="text-3xl font-bold">{value}</p>
    </motion.div>
  )
}

function AgentStatusCard({
  id,
  status,
  executions,
  delay,
}: {
  id: string
  status: string
  executions: number
  delay: number
}) {
  const statusColors = {
    idle: 'bg-slate-500',
    thinking: 'bg-yellow-500',
    executing: 'bg-green-500 animate-pulse',
    completed: 'bg-blue-500',
    failed: 'bg-red-500',
  }

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center justify-between p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
    >
      <div className="flex items-center gap-3">
        <div className={`w-2 h-2 rounded-full ${statusColors[status as keyof typeof statusColors] || 'bg-slate-500'}`} />
        <div>
          <p className="font-medium capitalize">{id}</p>
          <p className="text-xs text-slate-400">{executions} executions</p>
        </div>
      </div>
      <span className="text-xs px-2 py-1 rounded-full bg-white/10 capitalize">
        {status}
      </span>
    </motion.div>
  )
}

function ActivityItem({
  agent,
  action,
  time,
  delay,
}: {
  agent: string
  action: string
  time: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-start gap-3 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
    >
      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center flex-shrink-0">
        <Bot className="w-4 h-4" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{agent}</p>
        <p className="text-xs text-slate-400 truncate">{action}</p>
      </div>
      <span className="text-xs text-slate-500">{time}</span>
    </motion.div>
  )
}

function MetricCard({
  label,
  value,
  trend,
  positive,
}: {
  label: string
  value: string
  trend: string
  positive: boolean
}) {
  return (
    <div className="p-4 rounded-xl bg-white/5">
      <p className="text-sm text-slate-400 mb-2">{label}</p>
      <div className="flex items-end justify-between">
        <p className="text-2xl font-bold">{value}</p>
        <span
          className={`text-sm ${
            positive ? 'text-green-400' : 'text-red-400'
          }`}
        >
          {trend}
        </span>
      </div>
    </div>
  )
}
