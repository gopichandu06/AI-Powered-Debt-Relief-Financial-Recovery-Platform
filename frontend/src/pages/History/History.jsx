import { useState, useEffect } from 'react'
import { FileText, Target, Activity, Clock, TrendingDown } from 'lucide-react'
import { historyAPI } from '../../api/client'
import EmptyState from '../../components/ui/EmptyState'
import { SkeletonCard, SkeletonText } from '../../components/ui/LoadingSkeleton'
import './history.css'

const TABS = [
  { id: 'all', label: 'All Activity', icon: Activity },
  { id: 'settlements', label: 'Settlements', icon: Target },
  { id: 'letters', label: 'Letters', icon: FileText },
]

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

function timeAgo(dateStr) {
  const d = new Date(dateStr)
  const diff = Date.now() - d.getTime()
  const mins = Math.floor(diff / 60000)
  const hrs = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  if (hrs < 24) return `${hrs}h ago`
  if (days < 7) return `${days}d ago`
  return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
}

export default function History() {
  const [activeTab, setActiveTab] = useState('all')
  const [activity, setActivity] = useState([])
  const [settlements, setSettlements] = useState([])
  const [letters, setLetters] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      historyAPI.getActivity({ limit: 20 }).then((r) => setActivity(r.data?.activities || r.data || [])),
      historyAPI.getSettlements({ limit: 10 }).then((r) => setSettlements(r.data?.settlements || r.data || [])),
      historyAPI.getLetters({ limit: 10 }).then((r) => setLetters(r.data?.letters || r.data || [])),
      historyAPI.getSummary().then((r) => setSummary(r.data)),
    ])
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const ACTIVITY_ICONS = {
    settlement: Target,
    letter: FileText,
    loan_added: Activity,
    login: Activity,
    profile_update: Activity,
    default: Activity,
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">History</h1>
          <p className="page-subtitle">All your past actions and analyses</p>
        </div>
      </div>

      {/* Stats row */}
      <div className="history-stats">
        <div className="history-stat-card card">
          <div className="history-stat-icon" style={{ background: 'rgba(99,102,241,0.1)', color: 'var(--accent-primary)' }}>
            <Target size={20} />
          </div>
          <div>
            <p className="history-stat-value">{summary?.total_settlements || settlements.length}</p>
            <p className="history-stat-label">Settlements Run</p>
          </div>
        </div>
        <div className="history-stat-card card">
          <div className="history-stat-icon" style={{ background: 'rgba(16,185,129,0.1)', color: 'var(--accent-success)' }}>
            <FileText size={20} />
          </div>
          <div>
            <p className="history-stat-value">{summary?.total_letters || letters.length}</p>
            <p className="history-stat-label">Letters Generated</p>
          </div>
        </div>
        <div className="history-stat-card card">
          <div className="history-stat-icon" style={{ background: 'rgba(245,158,11,0.1)', color: 'var(--accent-warning)' }}>
            <TrendingDown size={20} />
          </div>
          <div>
            <p className="history-stat-value">{formatCurrency(summary?.total_potential_savings)}</p>
            <p className="history-stat-label">Potential Savings</p>
          </div>
        </div>
        <div className="history-stat-card card">
          <div className="history-stat-icon" style={{ background: 'rgba(239,68,68,0.1)', color: 'var(--accent-danger)' }}>
            <Activity size={20} />
          </div>
          <div>
            <p className="history-stat-value">{summary?.total_actions || activity.length}</p>
            <p className="history-stat-label">Total Actions</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="history-tabs">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            className={`history-tab ${activeTab === id ? 'active' : ''}`}
            onClick={() => setActiveTab(id)}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {loading ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="card" style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <div className="skeleton skeleton-circle" style={{ width: 40, height: 40, flexShrink: 0 }} />
              <SkeletonText lines={2} />
            </div>
          ))}
        </div>
      ) : (
        <>
          {/* All Activity */}
          {activeTab === 'all' && (
            <div className="history-timeline">
              {activity.length === 0 ? (
                <EmptyState icon="📋" title="No activity yet" description="Your actions will appear here as you use the app." />
              ) : (
                activity.map((item, i) => {
                  const type = item.activity_type || item.type || 'default'
                  const Icon = ACTIVITY_ICONS[type] || ACTIVITY_ICONS.default
                  return (
                    <div key={i} className="timeline-item">
                      <div className="timeline-connector">
                        <div className="timeline-dot">
                          <Icon size={14} />
                        </div>
                        {i < activity.length - 1 && <div className="timeline-line" />}
                      </div>
                      <div className="timeline-content card">
                        <div className="timeline-header">
                          <p className="timeline-text">{item.description || item.action || 'Action performed'}</p>
                          <span className="timeline-time">
                            <Clock size={11} />
                            {timeAgo(item.created_at || item.timestamp)}
                          </span>
                        </div>
                        {item.metadata && (
                          <p className="timeline-meta">
                            {typeof item.metadata === 'string' ? item.metadata : JSON.stringify(item.metadata)}
                          </p>
                        )}
                      </div>
                    </div>
                  )
                })
              )}
            </div>
          )}

          {/* Settlements */}
          {activeTab === 'settlements' && (
            <div className="history-settlements">
              {settlements.length === 0 ? (
                <EmptyState icon="🎯" title="No settlement analyses yet" description="Run your first settlement calculation to see history here." />
              ) : (
                settlements.map((s, i) => (
                  <div key={s.id || i} className="card settlement-history-card">
                    <div className="settlement-history-header">
                      <h4 className="settlement-history-title">Settlement Analysis #{s.id || i + 1}</h4>
                      <span className="timeline-time">
                        <Clock size={11} />
                        {timeAgo(s.created_at || s.timestamp)}
                      </span>
                    </div>
                    <div className="settlement-history-stats">
                      <div>
                        <span className="settlement-history-label">Total Outstanding</span>
                        <span className="settlement-history-value">{formatCurrency(s.total_outstanding)}</span>
                      </div>
                      <div>
                        <span className="settlement-history-label">Settlement Amount</span>
                        <span className="settlement-history-value">{formatCurrency(s.total_settlement_amount)}</span>
                      </div>
                      <div>
                        <span className="settlement-history-label">Potential Savings</span>
                        <span className="settlement-history-value" style={{ color: 'var(--accent-success)' }}>
                          {formatCurrency(s.total_potential_savings)}
                        </span>
                      </div>
                    </div>
                    {s.overall_strategy && (
                      <p className="settlement-history-strategy">{s.overall_strategy}</p>
                    )}
                  </div>
                ))
              )}
            </div>
          )}

          {/* Letters */}
          {activeTab === 'letters' && (
            <div className="history-letters">
              {letters.length === 0 ? (
                <EmptyState icon="📝" title="No letters generated yet" description="Generate your first settlement letter to see history here." />
              ) : (
                letters.map((letter, i) => (
                  <div key={letter.id || i} className="card letter-history-full-card">
                    <div className="letter-history-full-header">
                      <div className="letter-history-full-icon">
                        <FileText size={18} />
                      </div>
                      <div className="letter-history-full-info">
                        <h4 className="letter-history-full-title">
                          {letter.lender_name || letter.loan?.lender_name || 'Settlement Letter'}
                        </h4>
                        <div className="letter-history-full-meta">
                          <span className="badge badge-muted" style={{ textTransform: 'capitalize' }}>{letter.tone || 'professional'}</span>
                          <span className="timeline-time">
                            <Clock size={11} />
                            {timeAgo(letter.created_at || letter.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                    {letter.letter_content && (
                      <div className="letter-history-preview">
                        {letter.letter_content.slice(0, 200)}…
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
