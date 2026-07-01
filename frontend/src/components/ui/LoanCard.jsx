import { Pencil, Trash2, AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react'
import './LoanCard.css'

const STATUS_CONFIG = {
  active: { label: 'Active', icon: CheckCircle, className: 'badge-success' },
  overdue: { label: 'Overdue', icon: AlertTriangle, className: 'badge-warning' },
  defaulted: { label: 'Defaulted', icon: XCircle, className: 'badge-danger' },
  settled: { label: 'Settled', icon: CheckCircle, className: 'badge-info' },
  npa: { label: 'NPA', icon: XCircle, className: 'badge-danger' },
}

const TYPE_COLORS = {
  personal: 'badge-primary',
  home: 'badge-info',
  auto: 'badge-success',
  education: 'badge-warning',
  business: 'badge-muted',
  credit_card: 'badge-danger',
  other: 'badge-muted',
}

function formatCurrency(amount) {
  if (amount === undefined || amount === null) return '—'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function LoanCard({ loan, onEdit, onDelete }) {
  const status = STATUS_CONFIG[loan.status] || STATUS_CONFIG.active
  const StatusIcon = status.icon
  const loanType = (loan.loan_type || 'other').replace('_', ' ')
  const typeClass = TYPE_COLORS[loan.loan_type] || 'badge-muted'

  const paidAmount = (loan.original_amount || 0) - (loan.outstanding_balance || 0)
  const paidPercent = loan.original_amount
    ? Math.max(0, Math.min(100, (paidAmount / loan.original_amount) * 100))
    : 0

  return (
    <div className={`loan-card loan-card-${loan.status}`}>
      <div className="loan-card-header">
        <div className="loan-card-title-row">
          <h3 className="loan-card-lender">{loan.lender_name || 'Unknown Lender'}</h3>
          <div className="loan-card-badges">
            <span className={`badge ${typeClass}`}>{loanType}</span>
            <span className={`badge ${status.className}`}>
              <StatusIcon size={10} />
              {status.label}
            </span>
          </div>
        </div>
        <div className="loan-card-actions">
          <button className="btn btn-ghost btn-sm btn-icon" onClick={() => onEdit(loan)} title="Edit">
            <Pencil size={14} />
          </button>
          <button className="btn btn-ghost btn-sm btn-icon loan-delete-btn" onClick={() => onDelete(loan)} title="Delete">
            <Trash2 size={14} />
          </button>
        </div>
      </div>

      <div className="loan-card-balance">
        <span className="loan-balance-label">Outstanding Balance</span>
        <span className="loan-balance-value">{formatCurrency(loan.outstanding_balance)}</span>
      </div>

      <div className="loan-card-progress">
        <div className="loan-progress-labels">
          <span>Paid: {formatCurrency(paidAmount)}</span>
          <span>{paidPercent.toFixed(0)}%</span>
        </div>
        <div className="progress-bar-track">
          <div
            className="progress-bar-fill loan-progress-fill"
            style={{ width: `${paidPercent}%` }}
          />
        </div>
        <div className="loan-progress-labels">
          <span>Original: {formatCurrency(loan.original_amount)}</span>
          <span>Remaining: {formatCurrency(loan.outstanding_balance)}</span>
        </div>
      </div>

      <div className="loan-card-details">
        {loan.emi_amount && (
          <div className="loan-detail-item">
            <span className="loan-detail-label">Monthly EMI</span>
            <span className="loan-detail-value">{formatCurrency(loan.emi_amount)}</span>
          </div>
        )}
        {loan.interest_rate && (
          <div className="loan-detail-item">
            <span className="loan-detail-label">Interest Rate</span>
            <span className="loan-detail-value">{loan.interest_rate}% p.a.</span>
          </div>
        )}
        {loan.overdue_months > 0 && (
          <div className="loan-detail-item loan-overdue">
            <Clock size={12} />
            <span className="loan-detail-label">Overdue</span>
            <span className="loan-detail-value loan-overdue-value">{loan.overdue_months} months</span>
          </div>
        )}
        {loan.account_number && (
          <div className="loan-detail-item">
            <span className="loan-detail-label">Account #</span>
            <span className="loan-detail-value">{loan.account_number}</span>
          </div>
        )}
      </div>
    </div>
  )
}
