import { useEffect, useRef } from 'react'
import './HealthScoreRing.css'

function getScoreColor(score) {
  if (score >= 70) return '#10b981'
  if (score >= 40) return '#f59e0b'
  return '#ef4444'
}

function getScoreLabel(score) {
  if (score >= 80) return 'Excellent'
  if (score >= 70) return 'Good'
  if (score >= 55) return 'Fair'
  if (score >= 40) return 'Poor'
  return 'Critical'
}

export default function HealthScoreRing({ score = 0, size = 160, strokeWidth = 12, label = 'Financial Health' }) {
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius
  const fillRef = useRef(null)
  const clampedScore = Math.max(0, Math.min(100, score))
  const color = getScoreColor(clampedScore)
  const scoreLabel = getScoreLabel(clampedScore)

  useEffect(() => {
    if (!fillRef.current) return
    const offset = circumference - (clampedScore / 100) * circumference
    // Animate
    fillRef.current.style.transition = 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)'
    fillRef.current.style.strokeDashoffset = offset
  }, [clampedScore, circumference])

  return (
    <div className="health-ring-wrapper">
      <svg
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="health-ring-svg"
      >
        {/* Background track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="rgba(255,255,255,0.06)"
          strokeWidth={strokeWidth}
        />
        {/* Progress ring */}
        <circle
          ref={fillRef}
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          style={{ filter: `drop-shadow(0 0 8px ${color}60)` }}
        />
        {/* Score text */}
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          fill={color}
          fontSize={size * 0.22}
          fontWeight="700"
          fontFamily="Inter, sans-serif"
          dy="-0.1em"
        >
          {clampedScore}
        </text>
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="middle"
          fill="var(--text-muted)"
          fontSize={size * 0.1}
          fontFamily="Inter, sans-serif"
          dy="1.2em"
        >
          /100
        </text>
      </svg>
      <div className="health-ring-labels">
        <span className="health-ring-label" style={{ color }}>{scoreLabel}</span>
        <span className="health-ring-sublabel">{label}</span>
      </div>
    </div>
  )
}
