import { TrendingUp, TrendingDown, Minus } from 'lucide-react'
import './MetricCard.css'

export default function MetricCard({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'primary' }) {
  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp size={14} />
    if (trend === 'down') return <TrendingDown size={14} />
    return <Minus size={14} />
  }

  const getTrendClass = () => {
    if (trend === 'up') return 'metric-trend-up'
    if (trend === 'down') return 'metric-trend-down'
    return 'metric-trend-neutral'
  }

  return (
    <div className={`metric-card metric-card-${color}`}>
      <div className="metric-card-header">
        <span className="metric-card-title">{title}</span>
        {Icon && (
          <div className={`metric-card-icon metric-icon-${color}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="metric-card-value">{value}</div>
      <div className="metric-card-footer">
        {subtitle && <span className="metric-card-subtitle">{subtitle}</span>}
        {trendValue !== undefined && (
          <span className={`metric-trend ${getTrendClass()}`}>
            {getTrendIcon()}
            {trendValue}
          </span>
        )}
      </div>
    </div>
  )
}
