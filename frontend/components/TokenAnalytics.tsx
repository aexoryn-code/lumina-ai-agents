'use client'

import { motion } from 'framer-motion'
import { TrendingUp, TrendingDown, DollarSign, Zap, BarChart3 } from 'lucide-react'
import { useState, useEffect } from 'react'

interface TokenData {
  model: string
  tokens: number
  cost: number
  color: string
}

export default function TokenAnalytics() {
  const [tokenData, setTokenData] = useState<TokenData[]>([
    { model: 'GPT-4o', tokens: 15420, cost: 0.77, color: 'from-green-500 to-emerald-500' },
    { model: 'Claude Opus', tokens: 12350, cost: 1.85, color: 'from-orange-500 to-red-500' },
    { model: 'Claude Sonnet', tokens: 8920, cost: 0.27, color: 'from-blue-500 to-cyan-500' },
    { model: 'Gemini 2.0', tokens: 6540, cost: 0.07, color: 'from-purple-500 to-pink-500' },
    { model: 'DeepSeek', tokens: 4230, cost: 0.04, color: 'from-yellow-500 to-amber-500' },
  ])

  const totalTokens = tokenData.reduce((sum, d) => sum + d.tokens, 0)
  const totalCost = tokenData.reduce((sum, d) => sum + d.cost, 0)
  const maxTokens = Math.max(...tokenData.map(d => d.tokens))

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glassmorphism rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Total Tokens</span>
            <Zap className="w-4 h-4 text-yellow-400" />
          </div>
          <p className="text-3xl font-bold mb-1">
            {(totalTokens / 1000).toFixed(1)}K
          </p>
          <div className="flex items-center gap-1 text-sm">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-green-400">+12.5%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glassmorphism rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Total Cost</span>
            <DollarSign className="w-4 h-4 text-green-400" />
          </div>
          <p className="text-3xl font-bold mb-1">
            ${totalCost.toFixed(2)}
          </p>
          <div className="flex items-center gap-1 text-sm">
            <TrendingDown className="w-4 h-4 text-green-400" />
            <span className="text-green-400">-8.3%</span>
            <span className="text-slate-500">vs last week</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="glassmorphism rounded-xl p-6"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">Avg Cost/1K</span>
            <BarChart3 className="w-4 h-4 text-blue-400" />
          </div>
          <p className="text-3xl font-bold mb-1">
            ${(totalCost / (totalTokens / 1000)).toFixed(3)}
          </p>
          <div className="flex items-center gap-1 text-sm">
            <TrendingDown className="w-4 h-4 text-green-400" />
            <span className="text-green-400">-15.2%</span>
            <span className="text-slate-500">optimized</span>
          </div>
        </motion.div>
      </div>

      {/* Token Usage by Model */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glassmorphism rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold mb-6">Token Usage by Model</h3>
        <div className="space-y-4">
          {tokenData.map((data, index) => (
            <TokenBar
              key={data.model}
              data={data}
              maxTokens={maxTokens}
              delay={0.5 + index * 0.1}
            />
          ))}
        </div>
      </motion.div>

      {/* Cost Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0 }}
        className="glassmorphism rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold mb-6">Cost Breakdown</h3>
        <div className="space-y-3">
          {tokenData.map((data, index) => (
            <CostItem
              key={data.model}
              model={data.model}
              cost={data.cost}
              percentage={(data.cost / totalCost) * 100}
              color={data.color}
              delay={1.1 + index * 0.1}
            />
          ))}
        </div>
      </motion.div>

      {/* Optimization Tips */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.6 }}
        className="glassmorphism rounded-xl p-6"
      >
        <h3 className="text-lg font-semibold mb-4">Optimization Insights</h3>
        <div className="space-y-3">
          <InsightCard
            title="Token Efficiency"
            description="Your token usage is 23% more efficient than average"
            positive={true}
          />
          <InsightCard
            title="Cost Optimization"
            description="Consider using DeepSeek for simple tasks to reduce costs"
            positive={true}
          />
          <InsightCard
            title="Model Selection"
            description="GPT-4o usage increased 15% - review task routing"
            positive={false}
          />
        </div>
      </motion.div>
    </div>
  )
}

function TokenBar({
  data,
  maxTokens,
  delay,
}: {
  data: TokenData
  maxTokens: number
  delay: number
}) {
  const percentage = (data.tokens / maxTokens) * 100

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="space-y-2"
    >
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">{data.model}</span>
        <div className="flex items-center gap-3">
          <span className="text-slate-400">
            {(data.tokens / 1000).toFixed(1)}K tokens
          </span>
          <span className="text-slate-500">${data.cost.toFixed(2)}</span>
        </div>
      </div>
      <div className="h-3 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ delay: delay + 0.2, duration: 1, ease: 'easeOut' }}
          className={`h-full bg-gradient-to-r ${data.color} rounded-full`}
        />
      </div>
    </motion.div>
  )
}

function CostItem({
  model,
  cost,
  percentage,
  color,
  delay,
}: {
  model: string
  cost: number
  percentage: number
  color: string
  delay: number
}) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay }}
      className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
    >
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full bg-gradient-to-r ${color}`} />
        <span className="font-medium">{model}</span>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-slate-400">{percentage.toFixed(1)}%</span>
        <span className="font-semibold">${cost.toFixed(2)}</span>
      </div>
    </motion.div>
  )
}

function InsightCard({
  title,
  description,
  positive,
}: {
  title: string
  description: string
  positive: boolean
}) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-lg bg-white/5">
      <div
        className={`w-2 h-2 rounded-full mt-2 ${
          positive ? 'bg-green-400' : 'bg-yellow-400'
        }`}
      />
      <div className="flex-1">
        <p className="font-medium text-sm mb-1">{title}</p>
        <p className="text-xs text-slate-400">{description}</p>
      </div>
    </div>
  )
}
