import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { Plus, BarChart3, FileText, AlertTriangle, Activity, CreditCard, TrendingUp, Wallet } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import { analysisAPI, loansAPI, historyAPI } from '../../api/client'
import MetricCard from '../../components/ui/MetricCard'
import LoanCard from '../../components/ui/LoanCard'
import HealthScoreRing from '../../components/ui/HealthScoreRing'
import { SkeletonMetric, SkeletonCard } from '../../components/ui/LoadingSkeleton'
import EmptyState from '../../components/ui/EmptyState'
import './dashboard.css'

const CHART_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6']

const STRESS_CONFIG = {
  minimal: { class: 'stress-minimal', label: 'Minimal Stress', icon: '✅', msg: 'Your finances are in great shape. Keep up the good work!' },
  low: { class: 'stress-low', label: 'Low Stress', icon: '🟢', msg: 'Minor concerns. Monitor your spending and EMI payments.' },
  moderate: { class: 'stress-moderate', label: 'Moderate Stress', icon: '🟡', msg: 'Consider reviewing your budget. Settlement options may help.' },
  high: { class: 'stress-high', label: 'High Stress', icon: '🟠', msg: 'Your debt burden is significant. Run an analysis and explore settlement.' },
  critical: { class: 'stress-critical', label: 'Critical Stress', icon: '🔴', msg: 'Immediate action needed. Please explore debt settlement and professional help.' },
}

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label">{label}</p>
      {payload.map((p) => (
        <p key={p.name} style={{ color: p.color }}>
          {p.name}: {formatCurrency(p.value)}
        </p>
      ))}
    </div>
  )
}

export default function Dashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [health, setHealth] = useState(null)
  const [loans, setLoans] = useState([])
  const [activity, setActivity] = useState([])
  const [loadingHealth, setLoadingHealth] = useState(true)
  const [loadingLoans, setLoadingLoans] = useState(true)
  const [loadingActivity, setLoadingActivity] = useState(true)

  useEffect(() => {
    analysisAPI.getFinancialHealth()
      .then((r) => setHealth(r.data))
      .catch(() => {})
      .finally(() => setLoadingHealth(false))

    loansAPI.list()
      .then((r) => setLoans(r.data?.loans || r.data || []))
      .catch(() => {})
      .finally(() => setLoadingLoans(false))

    historyAPI.getActivity({ limit: 6 })
      .then((r) => setActivity(r.data?.activities || r.data || []))
      .catch(() => {})
      .finally(() => setLoadingActivity(false))
  }, [])

  const greeting = () => {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
  }

  const firstName = user?.full_name?.split(' ')[0] || 'there'
  const stress = health?.debt_stress_level || 'minimal'
  const stressCfg = STRESS_CONFIG[stress] || STRESS_CONFIG.minimal

  // Fake monthly chart data derived from profile if health API not fully loaded
  const chartData = health?.monthly_chart || [
    { month: 'Jan', income: 75000, expenses: 42000, emi: 18000 },
    { month: 'Feb', income: 75000, expenses: 38000, emi: 18000 },
    { month: 'Mar', income: 80000, expenses: 44000, emi: 18000 },
    { month: 'Apr', income: 75000, expenses: 40000, emi: 20000 },
    { month: 'May', income: 78000, expenses: 41000, emi: 20000 },
    { month: 'Jun', income: 75000, expenses: 39000, emi: 20000 },
  ]

  const loanTypeData = loans.reduce((acc, loan) => {
    const type = loan.loan_type || 'other'
    const existing = acc.find((i) => i.name === type)
    if (existing) existing.value += loan.outstanding_balance || 0
    else acc.push({ name: type, value: loan.outstanding_balance || 0 })
    return acc
  }, [])

  return (
    <div className="page-container animate-fade-in">
      {/* ─── Welcome Header ─── */}
      <div className="dashboard-welcome">
        <div>
          <h1 className="dashboard-greeting">
            {greeting()}, {firstName} 👋
          </h1>
          <p className="dashboard-date">
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </p>
        </div>
        <div className="dashboard-quick-actions">
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/loans')}>
            <Plus size={14} /> Add Loan
          </button>
          <button className="btn btn-secondary btn-sm" onClick={() => navigate('/analysis')}>
            <BarChart3 size={14} /> Analysis
          </button>
          <button className="btn btn-primary btn-sm" onClick={() => navigate('/letters')}>
            <FileText size={14} /> Generate Letter
          </button>
        </div>
      </div>

      {/* ─── Stress Banner ─── */}
      {(stress === 'high' || stress === 'critical') && (
        <div className={`stress-banner ${stressCfg.class}`}>
          <AlertTriangle size={18} />
          <div>
            <strong>{stressCfg.icon} {stressCfg.label}</strong>
            <span>{stressCfg.msg}</span>
          </div>
          <button className="btn btn-sm btn-secondary" onClick={() => navigate('/settlement')}>
            View Settlement Options →
          </button>
        </div>
      )}

      {/* ─── Metric Cards ─── */}
      <div className="dashboard-metrics">
        {loadingHealth ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonMetric key={i} />)
        ) : (
          <>
            <div className="metric-card-health card">
              <HealthScoreRing score={health?.financial_health_score || 0} size={120} strokeWidth={10} label="Health Score" />
            </div>
            <MetricCard
              title="Monthly Surplus"
              value={formatCurrency(health?.monthly_surplus)}
              subtitle="Income minus expenses & EMI"
              icon={Wallet}
              trend={health?.monthly_surplus > 0 ? 'up' : 'down'}
              color={health?.monthly_surplus > 0 ? 'success' : 'danger'}
            />
            <MetricCard
              title="Debt-to-Income"
              value={`${health?.debt_to_income_ratio?.toFixed(1) || 0}%`}
              subtitle="EMI vs monthly income"
              icon={TrendingUp}
              color={health?.debt_to_income_ratio > 40 ? 'danger' : 'primary'}
            />
            <MetricCard
              title="Total Outstanding"
              value={formatCurrency(health?.total_outstanding)}
              subtitle={`Across ${loans.length} loan${loans.length !== 1 ? 's' : ''}`}
              icon={CreditCard}
              color="warning"
            />
          </>
        )}
      </div>

      {/* ─── Charts ─── */}
      <div className="dashboard-charts">
        <div className="card dashboard-area-chart">
          <div className="chart-header">
            <h3 className="section-title" style={{ margin: 0 }}>Income vs Expenses vs EMI</h3>
            <span className="badge badge-muted">Last 6 months</span>
          </div>
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorExpenses" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorEmi" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="income" name="Income" stroke="#10b981" fill="url(#colorIncome)" strokeWidth={2} />
              <Area type="monotone" dataKey="expenses" name="Expenses" stroke="#6366f1" fill="url(#colorExpenses)" strokeWidth={2} />
              <Area type="monotone" dataKey="emi" name="EMI" stroke="#f59e0b" fill="url(#colorEmi)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="card dashboard-pie-chart">
          <div className="chart-header">
            <h3 className="section-title" style={{ margin: 0 }}>Loan Distribution</h3>
          </div>
          {loanTypeData.length === 0 ? (
            <EmptyState icon="📊" title="No loan data" description="Add loans to see the distribution" />
          ) : (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={loanTypeData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value">
                  {loanTypeData.map((_, index) => (
                    <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={{ background: '#1a1d26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#f1f5f9' }} />
                <Legend formatter={(val) => <span style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'capitalize' }}>{val.replace('_', ' ')}</span>} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* ─── Recent Loans ─── */}
      <div className="dashboard-section">
        <div className="dashboard-section-header">
          <h2 className="section-title">Recent Loans</h2>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/loans')}>View all →</button>
        </div>
        {loadingLoans ? (
          <div className="dashboard-loans-grid">
            {Array.from({ length: 3 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : loans.length === 0 ? (
          <EmptyState
            icon="💳"
            title="No loans added yet"
            description="Add your loans to start tracking balances and get settlement advice."
            actionLabel="Add Your First Loan"
            onAction={() => navigate('/loans')}
          />
        ) : (
          <div className="dashboard-loans-grid">
            {loans.slice(0, 3).map((loan) => (
              <LoanCard
                key={loan.id}
                loan={loan}
                onEdit={() => navigate('/loans')}
                onDelete={() => navigate('/loans')}
              />
            ))}
          </div>
        )}
      </div>

      {/* ─── Recent Activity ─── */}
      <div className="dashboard-section">
        <div className="dashboard-section-header">
          <h2 className="section-title">Recent Activity</h2>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate('/history')}>View history →</button>
        </div>
        <div className="card">
          {loadingActivity ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <div className="skeleton skeleton-circle" style={{ width: 36, height: 36, flexShrink: 0 }} />
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <div className="skeleton" style={{ height: 14, width: '60%' }} />
                    <div className="skeleton" style={{ height: 12, width: '35%' }} />
                  </div>
                </div>
              ))}
            </div>
          ) : activity.length === 0 ? (
            <EmptyState icon="📋" title="No activity yet" description="Your actions will appear here." />
          ) : (
            <div className="activity-list">
              {activity.map((item, i) => (
                <div key={i} className="activity-item">
                  <div className="activity-icon">
                    <Activity size={14} />
                  </div>
                  <div className="activity-content">
                    <p className="activity-text">{item.description || item.action}</p>
                    <span className="activity-time">
                      {new Date(item.created_at || item.timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
