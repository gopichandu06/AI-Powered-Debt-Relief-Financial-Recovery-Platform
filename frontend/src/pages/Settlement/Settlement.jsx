import { useState } from 'react'
import { Target, Sparkles, AlertTriangle, CheckCircle, TrendingDown, ArrowRight, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { settlementAPI } from '../../api/client'
import EmptyState from '../../components/ui/EmptyState'
import './settlement.css'

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

const PRIORITY_COLORS = {
  1: { bg: 'rgba(239,68,68,0.1)', border: 'rgba(239,68,68,0.2)', color: '#ef4444', label: 'Critical Priority' },
  2: { bg: 'rgba(245,158,11,0.1)', border: 'rgba(245,158,11,0.2)', color: '#f59e0b', label: 'High Priority' },
  3: { bg: 'rgba(99,102,241,0.1)', border: 'rgba(99,102,241,0.2)', color: '#6366f1', label: 'Medium Priority' },
  4: { bg: 'rgba(16,185,129,0.1)', border: 'rgba(16,185,129,0.2)', color: '#10b981', label: 'Low Priority' },
}

function getPriorityCfg(rank) {
  return PRIORITY_COLORS[Math.min(rank, 4)] || PRIORITY_COLORS[4]
}

export default function Settlement() {
  const [results, setResults] = useState(null)
  const [aiAdvice, setAiAdvice] = useState(null)
  const [isCalculating, setIsCalculating] = useState(false)
  const [isGettingAdvice, setIsGettingAdvice] = useState(false)

  const handleCalculate = async () => {
    setIsCalculating(true)
    setAiAdvice(null)
    try {
      const res = await settlementAPI.calculate()
      setResults(res.data)
      toast.success('Settlement calculations ready!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to calculate settlements. Ensure you have profile & loans added.')
    } finally {
      setIsCalculating(false)
    }
  }

  const handleGetAdvice = async () => {
    if (!results) return
    setIsGettingAdvice(true)
    try {
      const res = await settlementAPI.getAIAdvice({ settlement_data: results })
      setAiAdvice(res.data)
      toast.success('AI advice generated!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to get AI advice')
    } finally {
      setIsGettingAdvice(false)
    }
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Debt Settlement</h1>
          <p className="page-subtitle">Calculate settlement offers and get AI-powered negotiation strategies</p>
        </div>
      </div>

      {/* Info banner */}
      <div className="settlement-info-banner">
        <div className="settlement-info-icon">
          <Target size={24} />
        </div>
        <div className="settlement-info-content">
          <h3>What is Debt Settlement?</h3>
          <p>
            Debt settlement is a negotiation process where you work with your lender to pay a lump sum
            that is less than the full amount owed. Lenders often agree when accounts are overdue or in default,
            as it guarantees some recovery. Our AI analyzes your situation to find the best settlement percentages
            and strategies for each loan.
          </p>
        </div>
      </div>

      {/* Calculate button */}
      {!results && (
        <div className="settlement-cta">
          <div className="settlement-cta-content">
            <h2>Ready to calculate your settlement options?</h2>
            <p>We'll analyze each of your loans and provide personalized settlement recommendations based on your financial situation.</p>
            <button
              className="btn btn-primary btn-lg"
              onClick={handleCalculate}
              disabled={isCalculating}
            >
              {isCalculating ? (
                <><span className="spinner" /> Calculating…</>
              ) : (
                <><Target size={18} /> Calculate Settlement Options</>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Results */}
      {results && (
        <div className="settlement-results animate-slide-up">
          {/* Savings summary */}
          <div className="settlement-savings-card">
            <div className="settlement-savings-icon">
              <TrendingDown size={32} />
            </div>
            <div>
              <p className="settlement-savings-label">Total Potential Savings</p>
              <p className="settlement-savings-value">{formatCurrency(results.total_potential_savings)}</p>
              <p className="settlement-savings-sub">
                Settle for {formatCurrency(results.total_settlement_amount)} instead of {formatCurrency(results.total_outstanding)}
              </p>
            </div>
            <button
              className="btn btn-success settlement-advice-btn"
              onClick={handleGetAdvice}
              disabled={isGettingAdvice}
            >
              {isGettingAdvice ? (
                <><span className="spinner" /> Getting AI Advice…</>
              ) : (
                <><Sparkles size={16} /> Get AI Advice</>
              )}
            </button>
          </div>

          {/* Strategy recommendation */}
          {results.overall_strategy && (
            <div className="card settlement-strategy">
              <h3 className="section-title">Overall Strategy</h3>
              <p className="settlement-strategy-text">{results.overall_strategy}</p>
            </div>
          )}

          {/* Per loan cards */}
          <h2 className="section-title" style={{ marginBottom: 'var(--space-md)' }}>Settlement Plan by Loan</h2>
          <div className="settlement-loans-grid">
            {(results.loan_settlements || results.settlements || []).map((ls, i) => {
              const cfg = getPriorityCfg(ls.priority_rank || i + 1)
              return (
                <div
                  key={ls.loan_id || i}
                  className="settlement-loan-card"
                  style={{
                    background: cfg.bg,
                    borderColor: cfg.border,
                  }}
                >
                  <div className="settlement-loan-header">
                    <div>
                      <h3 className="settlement-loan-lender">{ls.lender_name}</h3>
                      <span className="badge badge-muted" style={{ textTransform: 'capitalize' }}>{ls.loan_type?.replace('_', ' ')}</span>
                    </div>
                    <div className="settlement-priority-badge" style={{ color: cfg.color, borderColor: cfg.border }}>
                      #{ls.priority_rank || i + 1} {cfg.label}
                    </div>
                  </div>

                  <div className="settlement-loan-amounts">
                    <div className="settlement-amount-item">
                      <span className="settlement-amount-label">Outstanding</span>
                      <span className="settlement-amount-value">{formatCurrency(ls.outstanding_balance)}</span>
                    </div>
                    <ArrowRight size={20} style={{ color: 'var(--text-muted)', alignSelf: 'flex-end', marginBottom: '4px' }} />
                    <div className="settlement-amount-item">
                      <span className="settlement-amount-label">Settle For</span>
                      <span className="settlement-amount-value" style={{ color: cfg.color }}>
                        {formatCurrency(ls.settlement_amount)}
                      </span>
                    </div>
                    <div className="settlement-amount-item">
                      <span className="settlement-amount-label">You Save</span>
                      <span className="settlement-amount-value" style={{ color: '#10b981' }}>
                        {formatCurrency(ls.potential_savings)}
                      </span>
                    </div>
                  </div>

                  <div className="settlement-loan-meta">
                    <div className="settlement-pct">
                      <span>Settlement at <strong style={{ color: cfg.color }}>{ls.settlement_percentage}%</strong> of outstanding</span>
                    </div>
                    {ls.strategy && (
                      <p className="settlement-loan-strategy">{ls.strategy}</p>
                    )}
                  </div>
                </div>
              )
            })}
          </div>

          {/* Recalculate */}
          <button className="btn btn-secondary" onClick={handleCalculate} disabled={isCalculating} style={{ marginTop: 'var(--space-lg)' }}>
            <Target size={16} /> Recalculate
          </button>
        </div>
      )}

      {/* AI Advice panel */}
      {aiAdvice && (
        <div className="card settlement-ai-panel animate-slide-up">
          <div className="settlement-ai-header">
            <div className="settlement-ai-icon">
              <Sparkles size={20} />
            </div>
            <h2 className="section-title" style={{ margin: 0 }}>AI-Powered Settlement Advice</h2>
          </div>

          {aiAdvice.strategies && aiAdvice.strategies.length > 0 && (
            <div className="settlement-ai-section">
              <h4 className="settlement-ai-section-title">Recommended Strategies</h4>
              <ul className="settlement-strategies-list">
                {aiAdvice.strategies.map((s, i) => (
                  <li key={i} className="settlement-strategy-item">
                    <CheckCircle size={16} style={{ color: '#10b981', flexShrink: 0, marginTop: 2 }} />
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {aiAdvice.warnings && aiAdvice.warnings.length > 0 && (
            <div className="settlement-ai-section">
              <h4 className="settlement-ai-section-title">Important Warnings</h4>
              <ul className="settlement-strategies-list">
                {aiAdvice.warnings.map((w, i) => (
                  <li key={i} className="settlement-strategy-item warning">
                    <AlertTriangle size={16} style={{ color: '#f59e0b', flexShrink: 0, marginTop: 2 }} />
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {aiAdvice.recovery_timeline && (
            <div className="settlement-ai-section">
              <h4 className="settlement-ai-section-title">
                <Clock size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                Recovery Timeline
              </h4>
              <p className="settlement-ai-text">{aiAdvice.recovery_timeline}</p>
            </div>
          )}

          {aiAdvice.advice && (
            <div className="settlement-ai-section">
              <p className="settlement-ai-text">{aiAdvice.advice}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
