'use client'

import { motion } from 'framer-motion'
import { useState, useEffect } from 'react'

interface DataPoint {
  label: string
  value: number
}

interface PerformanceGraphProps {
  title: string
  data: DataPoint[]
  color?: string
  maxValue?: number
}

export default function PerformanceGraph({
  title,
  data,
  color = 'from-blue-500 to-cyan-500',
  maxValue,
}: PerformanceGraphProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)
  const max = maxValue || Math.max(...data.map(d => d.value))

  return (
    <div className="glassmorphism rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-6">{title}</h3>

      {/* Graph */}
      <div className="relative h-64 mb-4">
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-slate-500">
          <span>{max}</span>
          <span>{(max * 0.75).toFixed(0)}</span>
          <span>{(max * 0.5).toFixed(0)}</span>
          <span>{(max * 0.25).toFixed(0)}</span>
          <span>0</span>
        </div>

        {/* Grid lines */}
        <div className="absolute left-12 right-0 top-0 bottom-0">
          {[0, 25, 50, 75, 100].map((percent) => (
            <div
              key={percent}
              className="absolute left-0 right-0 border-t border-white/5"
              style={{ top: `${100 - percent}%` }}
            />
          ))}
        </div>

        {/* Bars */}
        <div className="absolute left-12 right-0 top-0 bottom-0 flex items-end justify-around gap-2">
          {data.map((point, index) => {
            const height = (point.value / max) * 100
            const isHovered = hoveredIndex === index

            return (
              <div
                key={index}
                className="flex-1 flex flex-col items-center justify-end"
                onMouseEnter={() => setHoveredIndex(index)}
                onMouseLeave={() => setHoveredIndex(null)}
              >
                {/* Value tooltip */}
                {isHovered && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mb-2 px-2 py-1 rounded bg-black/80 text-xs font-semibold whitespace-nowrap"
                  >
                    {point.value}
                  </motion.div>
                )}

                {/* Bar */}
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: `${height}%` }}
                  transition={{
                    delay: index * 0.1,
                    duration: 0.8,
                    ease: 'easeOut',
                  }}
                  className={`w-full rounded-t-lg bg-gradient-to-t ${color} ${
                    isHovered ? 'opacity-100' : 'opacity-80'
                  } transition-opacity cursor-pointer relative overflow-hidden`}
                >
                  {/* Shimmer effect */}
                  <motion.div
                    animate={{
                      x: ['-100%', '100%'],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                      ease: 'linear',
                    }}
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent"
                  />
                </motion.div>
              </div>
            )
          })}
        </div>
      </div>

      {/* X-axis labels */}
      <div className="flex items-center justify-around gap-2 ml-12">
        {data.map((point, index) => (
          <div
            key={index}
            className="flex-1 text-center text-xs text-slate-400 truncate"
          >
            {point.label}
          </div>
        ))}
      </div>
    </div>
  )
}

// Line graph variant
export function LineGraph({
  title,
  data,
  color = 'from-purple-500 to-pink-500',
}: PerformanceGraphProps) {
  const max = Math.max(...data.map(d => d.value))
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null)

  // Calculate path for line
  const points = data.map((point, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - (point.value / max) * 100
    return { x, y, value: point.value, label: point.label }
  })

  const pathD = points
    .map((point, index) => {
      if (index === 0) return `M ${point.x} ${point.y}`
      return `L ${point.x} ${point.y}`
    })
    .join(' ')

  return (
    <div className="glassmorphism rounded-xl p-6">
      <h3 className="text-lg font-semibold mb-6">{title}</h3>

      <div className="relative h-64">
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-xs text-slate-500">
          <span>{max}</span>
          <span>{(max * 0.75).toFixed(0)}</span>
          <span>{(max * 0.5).toFixed(0)}</span>
          <span>{(max * 0.25).toFixed(0)}</span>
          <span>0</span>
        </div>

        {/* Grid */}
        <div className="absolute left-12 right-0 top-0 bottom-0">
          {[0, 25, 50, 75, 100].map((percent) => (
            <div
              key={percent}
              className="absolute left-0 right-0 border-t border-white/5"
              style={{ top: `${100 - percent}%` }}
            />
          ))}
        </div>

        {/* Line graph */}
        <svg
          className="absolute left-12 right-0 top-0 bottom-0 w-full h-full"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          {/* Area under line */}
          <motion.path
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 0.2 }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            d={`${pathD} L 100 100 L 0 100 Z`}
            className={`fill-gradient-to-t ${color}`}
            style={{
              fill: 'url(#gradient)',
            }}
          />

          {/* Line */}
          <motion.path
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.5, ease: 'easeOut' }}
            d={pathD}
            fill="none"
            stroke="url(#lineGradient)"
            strokeWidth="2"
            strokeLinecap="round"
          />

          {/* Gradient definitions */}
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor="rgb(59, 130, 246)" stopOpacity="0.5" />
              <stop offset="100%" stopColor="rgb(59, 130, 246)" stopOpacity="0" />
            </linearGradient>
            <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="rgb(168, 85, 247)" />
              <stop offset="100%" stopColor="rgb(236, 72, 153)" />
            </linearGradient>
          </defs>

          {/* Data points */}
          {points.map((point, index) => (
            <motion.circle
              key={index}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 1.5 + index * 0.1, duration: 0.3 }}
              cx={point.x}
              cy={point.y}
              r="2"
              fill="white"
              className="cursor-pointer"
              onMouseEnter={() => setHoveredIndex(index)}
              onMouseLeave={() => setHoveredIndex(null)}
            />
          ))}
        </svg>

        {/* Tooltips */}
        {hoveredIndex !== null && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute px-3 py-2 rounded-lg bg-black/90 text-sm font-semibold pointer-events-none"
            style={{
              left: `${12 + (hoveredIndex / (data.length - 1)) * 88}%`,
              top: `${100 - (data[hoveredIndex].value / max) * 100}%`,
              transform: 'translate(-50%, -120%)',
            }}
          >
            <div className="text-xs text-slate-400 mb-1">
              {data[hoveredIndex].label}
            </div>
            <div>{data[hoveredIndex].value}</div>
          </motion.div>
        )}
      </div>

      {/* X-axis labels */}
      <div className="flex items-center justify-between mt-4 ml-12 text-xs text-slate-400">
        <span>{data[0]?.label}</span>
        <span>{data[Math.floor(data.length / 2)]?.label}</span>
        <span>{data[data.length - 1]?.label}</span>
      </div>
    </div>
  )
}
