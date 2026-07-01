import { useState, useEffect } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts'
import { RefreshCw, TrendingUp, AlertCircle, CheckCircle, Info } from 'lucide-react'
import toast from 'react-hot-toast'
import { analysisAPI } from '../../api/client'
import HealthScoreRing from '../../components/ui/HealthScoreRing'
import MetricCard from '../../components/ui/MetricCard'
import { SkeletonMetric } from '../../components/ui/LoadingSkeleton'
import EmptyState from '../../components/ui/EmptyState'
import './analysis.css'

const PIE_COLORS = ['#6366f1', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#3b82f6']

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

const RISK_CONFIG = {
  low: { label: 'Low Risk', class: 'badge-success', icon: CheckCircle },
  medium: { label: 'Medium Risk', class: 'badge-warning', icon: AlertCircle },
  high: { label: 'High Risk', class: 'badge-danger', icon: AlertCircle },
  very_high: { label: 'Very High Risk', class: 'badge-danger', icon: AlertCircle },
}

const STRESS_CONFIG = {
  minimal: { label: 'Minimal', color: '#10b981' },
  low: { label: 'Low', color: '#10b981' },
  moderate: { label: 'Moderate', color: '#f59e0b' },
  high: { label: 'High', color: '#f59e0b' },
  critical: { label: 'Critical', color: '#ef4444' },
}

const MetricGuide = ({ items }) => (
  <div className="analysis-guide">
    {items.map((item) => (
      <div key={item.label} className="analysis-guide-item">
        <div className="analysis-guide-label">
          <Info size={14} />
          <strong>{item.label}</strong>
        </div>
        <p>{item.desc}</p>
      </div>
    ))}
  </div>
)

export default function Analysis() {
  const [health, setHealth] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)

  const fetch = (refresh = false) => {
    if (refresh) setIsRefreshing(true)
    else setIsLoading(true)
    analysisAPI.getFinancialHealth()
      .then((r) => setHealth(r.data))
      .catch(() => toast.error('Failed to load analysis'))
      .finally(() => { setIsLoading(false); setIsRefreshing(false) })
  }

  useEffect(() => { fetch() }, [])

  const riskCfg = health ? (RISK_CONFIG[health.risk_category] || RISK_CONFIG.medium) : null
  const stressCfg = health ? (STRESS_CONFIG[health.debt_stress_level] || STRESS_CONFIG.minimal) : null

  const loanBalanceData = health?.loan_details?.map((l) => ({
    name: l.lender_name?.split(' ')[0] || 'Loan',
    outstanding: l.outstanding_balance,
    emi: l.emi_amount,
  })) || []

  const loanTypeData = health?.loan_type_distribution || []

  const surplusData = [
    { name: 'Income', value: health?.monthly_income || 0, fill: '#10b981' },
    { name: 'Expenses', value: health?.monthly_expenses || 0, fill: '#6366f1' },
    { name: 'EMI', value: health?.total_emi || 0, fill: '#f59e0b' },
    { name: 'Surplus', value: Math.max(0, health?.monthly_surplus || 0), fill: '#8b5cf6' },
  ]

  if (isLoading) {
    return (
      <div className="page-container">
        <div className="page-header">
          <h1 className="page-title">Financial Analysis</h1>
        </div>
        <div className="analysis-metrics-grid">
          {Array.from({ length: 5 }).map((_, i) => <SkeletonMetric key={i} />)}
        </div>
      </div>
    )
  }

  if (!health) {
    return (
      <div className="page-container">
        <EmptyState
          icon="📊"
          title="No analysis available"
          description="Add your financial profile and loans to run an analysis."
        />
      </div>
    )
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Financial Analysis</h1>
          <p className="page-subtitle">AI-driven insights into your debt situation</p>
        </div>
        <button className="btn btn-secondary" onClick={() => fetch(true)} disabled={isRefreshing}>
          <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
          Refresh Analysis
        </button>
      </div>

      {/* ─── Health Score Hero ─── */}
      <div className="analysis-hero card">
        <div className="analysis-hero-score">
          <HealthScoreRing score={health.financial_health_score || 0} size={180} strokeWidth={14} />
        </div>
        <div className="analysis-hero-info">
          <div className="analysis-hero-badges">
            {riskCfg && (
              <span className={`badge ${riskCfg.class}`}>
                <riskCfg.icon size={12} />
                {riskCfg.label}
              </span>
            )}
            {stressCfg && (
              <span className="badge badge-muted">
                Debt Stress: <strong style={{ color: stressCfg.color, marginLeft: '4px' }}>{stressCfg.label}</strong>
              </span>
            )}
          </div>
          <h2 className="analysis-hero-title">Financial Health Overview</h2>
          <p className="analysis-hero-desc">
            Your financial health score is calculated based on your debt-to-income ratio,
            EMI obligations, credit score, and repayment history.
          </p>
          <div className="analysis-hero-metrics">
            <div className="analysis-mini-metric">
              <span className="analysis-mini-label">Monthly Income</span>
              <span className="analysis-mini-value" style={{ color: '#10b981' }}>{formatCurrency(health.monthly_income)}</span>
            </div>
            <div className="analysis-mini-metric">
              <span className="analysis-mini-label">Total EMI</span>
              <span className="analysis-mini-value" style={{ color: '#f59e0b' }}>{formatCurrency(health.total_emi)}</span>
            </div>
            <div className="analysis-mini-metric">
              <span className="analysis-mini-label">Monthly Surplus</span>
              <span className="analysis-mini-value" style={{ color: health.monthly_surplus >= 0 ? '#10b981' : '#ef4444' }}>
                {formatCurrency(health.monthly_surplus)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ─── Metrics Grid ─── */}
      <div className="analysis-metrics-grid">
        <MetricCard
          title="Debt-to-Income Ratio"
          value={`${health.debt_to_income_ratio?.toFixed(1) || 0}%`}
          subtitle={health.debt_to_income_ratio > 40 ? 'Above safe threshold (40%)' : 'Within safe range'}
          color={health.debt_to_income_ratio > 40 ? 'danger' : 'success'}
        />
        <MetricCard
          title="EMI-to-Income Ratio"
          value={`${health.emi_to_income_ratio?.toFixed(1) || 0}%`}
          subtitle={health.emi_to_income_ratio > 50 ? 'High EMI burden' : 'Manageable'}
          color={health.emi_to_income_ratio > 50 ? 'danger' : 'primary'}
        />
        <MetricCard
          title="Monthly Surplus"
          value={formatCurrency(health.monthly_surplus)}
          subtitle="After expenses & EMIs"
          color={health.monthly_surplus > 0 ? 'success' : 'danger'}
        />
        <MetricCard
          title="Disposable Income"
          value={formatCurrency(health.disposable_income || health.monthly_surplus)}
          subtitle="Available after all obligations"
          color="primary"
        />
        <MetricCard
          title="Total Outstanding"
          value={formatCurrency(health.total_outstanding)}
          subtitle={`Across ${health.total_loans || 0} loans`}
          color="warning"
        />
      </div>

      {/* ─── Charts ─── */}
      <div className="analysis-charts-grid">
        {/* Bar chart: Outstanding by loan */}
        {loanBalanceData.length > 0 && (
          <div className="card">
            <h3 className="section-title">Outstanding Balance by Loan</h3>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={loanBalanceData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="name" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip
                  formatter={(v) => formatCurrency(v)}
                  contentStyle={{ background: '#1a1d26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#f1f5f9' }}
                />
                <Bar dataKey="outstanding" name="Outstanding" fill="#6366f1" radius={[4, 4, 0, 0]} />
                <Bar dataKey="emi" name="EMI" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Pie chart: loan type distribution */}
        {loanTypeData.length > 0 && (
          <div className="card">
            <h3 className="section-title">Loan Type Distribution</h3>
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie data={loanTypeData} cx="50%" cy="50%" innerRadius={55} outerRadius={85} paddingAngle={4} dataKey="value">
                  {loanTypeData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v) => formatCurrency(v)} contentStyle={{ background: '#1a1d26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#f1f5f9' }} />
                <Legend formatter={(v) => <span style={{ color: '#94a3b8', fontSize: '11px', textTransform: 'capitalize' }}>{v.replace('_', ' ')}</span>} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Bar chart: EMI vs Surplus */}
        <div className="card analysis-surplus-chart">
          <h3 className="section-title">Monthly Cash Flow</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={surplusData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
              <YAxis type="category" dataKey="name" stroke="#475569" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip formatter={(v) => formatCurrency(v)} contentStyle={{ background: '#1a1d26', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '8px', color: '#f1f5f9' }} />
              <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                {surplusData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ─── Loan Priority Table ─── */}
      {health.loan_details && health.loan_details.length > 0 && (
        <div className="card analysis-priority">
          <h3 className="section-title">Loan Settlement Priority</h3>
          <p className="analysis-priority-desc">Ranked by settlement eligibility and priority score</p>
          <div className="analysis-table-wrapper">
            <table className="analysis-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Lender</th>
                  <th>Type</th>
                  <th>Outstanding</th>
                  <th>Status</th>
                  <th>Overdue</th>
                  <th>Settlement Eligible</th>
                </tr>
              </thead>
              <tbody>
                {health.loan_details.map((loan, i) => (
                  <tr key={loan.id || i}>
                    <td><span className="analysis-rank">{i + 1}</span></td>
                    <td><strong>{loan.lender_name}</strong></td>
                    <td><span className="badge badge-primary" style={{ textTransform: 'capitalize' }}>{loan.loan_type?.replace('_', ' ')}</span></td>
                    <td>{formatCurrency(loan.outstanding_balance)}</td>
                    <td>
                      <span className={`badge ${loan.status === 'active' ? 'badge-success' : loan.status === 'overdue' ? 'badge-warning' : 'badge-danger'}`}>
                        {loan.status}
                      </span>
                    </td>
                    <td>{loan.overdue_months > 0 ? `${loan.overdue_months}m` : '—'}</td>
                    <td>
                      {loan.overdue_months >= 3 ? (
                        <span className="badge badge-success">✓ Eligible</span>
                      ) : (
                        <span className="badge badge-muted">—</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ─── Interpretation Guide ─── */}
      <div className="card">
        <h3 className="section-title">Understanding Your Metrics</h3>
        <MetricGuide items={[
          { label: 'Debt-to-Income (DTI)', desc: 'Total monthly debt payments ÷ gross monthly income. Below 36% is healthy; above 50% is a concern.' },
          { label: 'EMI-to-Income', desc: 'Total EMI payments as percentage of income. Lenders prefer below 40-50%. Above 60% signals high stress.' },
          { label: 'Monthly Surplus', desc: 'What remains after income minus expenses and EMIs. Positive surplus = financial buffer. Negative = deficit.' },
          { label: 'Financial Health Score', desc: 'Composite score (0-100) combining DTI, credit score, overdue months, and surplus ratio. Higher is better.' },
        ]} />
      </div>
    </div>
  )
}
