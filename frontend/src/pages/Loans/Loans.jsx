import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Plus, Filter, Search } from 'lucide-react'
import toast from 'react-hot-toast'
import { loansAPI } from '../../api/client'
import LoanCard from '../../components/ui/LoanCard'
import Modal from '../../components/ui/Modal'
import EmptyState from '../../components/ui/EmptyState'
import { SkeletonCard } from '../../components/ui/LoadingSkeleton'
import './loans.css'

const LOAN_TYPES = [
  { value: 'personal', label: 'Personal Loan' },
  { value: 'home', label: 'Home Loan' },
  { value: 'auto', label: 'Auto Loan' },
  { value: 'education', label: 'Education Loan' },
  { value: 'business', label: 'Business Loan' },
  { value: 'credit_card', label: 'Credit Card' },
  { value: 'other', label: 'Other' },
]

const STATUSES = [
  { value: 'active', label: 'Active' },
  { value: 'overdue', label: 'Overdue' },
  { value: 'defaulted', label: 'Defaulted' },
  { value: 'npa', label: 'NPA' },
  { value: 'settled', label: 'Settled' },
]

function formatCurrency(n) {
  if (!n && n !== 0) return '—'
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(n)
}

const defaultValues = {
  lender_name: '', loan_type: 'personal', original_amount: '', outstanding_balance: '',
  interest_rate: '', emi_amount: '', overdue_months: 0, status: 'active', account_number: '',
}

export default function Loans() {
  const [loans, setLoans] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [modalOpen, setModalOpen] = useState(false)
  const [deleteModal, setDeleteModal] = useState(false)
  const [editingLoan, setEditingLoan] = useState(null)
  const [deletingLoan, setDeletingLoan] = useState(null)
  const [filter, setFilter] = useState('all')
  const [search, setSearch] = useState('')

  const { register, handleSubmit, reset, setValue, formState: { errors } } = useForm({ defaultValues })

  const fetchLoans = () => {
    setIsLoading(true)
    loansAPI.list()
      .then((r) => setLoans(r.data?.loans || r.data || []))
      .catch(() => toast.error('Failed to load loans'))
      .finally(() => setIsLoading(false))
  }

  useEffect(() => { fetchLoans() }, [])

  const openAdd = () => {
    reset(defaultValues)
    setEditingLoan(null)
    setModalOpen(true)
  }

  const openEdit = (loan) => {
    setEditingLoan(loan)
    Object.entries(loan).forEach(([k, v]) => setValue(k, v ?? ''))
    setModalOpen(true)
  }

  const openDelete = (loan) => {
    setDeletingLoan(loan)
    setDeleteModal(true)
  }

  const onSubmit = async (data) => {
    setIsSaving(true)
    try {
      const payload = {
        ...data,
        original_amount: Number(data.original_amount),
        outstanding_balance: Number(data.outstanding_balance),
        interest_rate: Number(data.interest_rate),
        emi_amount: Number(data.emi_amount),
        overdue_months: Number(data.overdue_months || 0),
      }
      if (editingLoan) {
        await loansAPI.update(editingLoan.id, payload)
        toast.success('Loan updated!')
      } else {
        await loansAPI.create(payload)
        toast.success('Loan added!')
      }
      setModalOpen(false)
      fetchLoans()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save loan')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!deletingLoan) return
    try {
      await loansAPI.delete(deletingLoan.id)
      toast.success('Loan deleted')
      setDeleteModal(false)
      setDeletingLoan(null)
      fetchLoans()
    } catch (err) {
      toast.error('Failed to delete loan')
    }
  }

  const filtered = loans.filter((l) => {
    const matchFilter = filter === 'all' || l.status === filter
    const matchSearch = !search || l.lender_name?.toLowerCase().includes(search.toLowerCase())
    return matchFilter && matchSearch
  })

  const totalOutstanding = loans.reduce((s, l) => s + (l.outstanding_balance || 0), 0)
  const totalEmi = loans.reduce((s, l) => s + (l.emi_amount || 0), 0)

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">My Loans</h1>
          <p className="page-subtitle">Track and manage all your debt obligations</p>
        </div>
        <button className="btn btn-primary" onClick={openAdd}>
          <Plus size={16} /> Add Loan
        </button>
      </div>

      {/* Summary row */}
      {loans.length > 0 && (
        <div className="loans-summary">
          <div className="loans-summary-item">
            <span className="loans-summary-label">Total Loans</span>
            <span className="loans-summary-value">{loans.length}</span>
          </div>
          <div className="loans-summary-item">
            <span className="loans-summary-label">Total Outstanding</span>
            <span className="loans-summary-value loans-summary-danger">{formatCurrency(totalOutstanding)}</span>
          </div>
          <div className="loans-summary-item">
            <span className="loans-summary-label">Total Monthly EMI</span>
            <span className="loans-summary-value loans-summary-warning">{formatCurrency(totalEmi)}</span>
          </div>
          <div className="loans-summary-item">
            <span className="loans-summary-label">Overdue</span>
            <span className="loans-summary-value loans-summary-danger">
              {loans.filter((l) => l.status === 'overdue' || l.status === 'defaulted' || l.status === 'npa').length}
            </span>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="loans-filters">
        <div className="loans-search-wrapper">
          <Search size={16} className="loans-search-icon" />
          <input
            type="text"
            className="form-input loans-search"
            placeholder="Search by lender…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="loans-filter-tabs">
          {['all', 'active', 'overdue', 'defaulted', 'settled'].map((s) => (
            <button
              key={s}
              className={`loans-filter-tab ${filter === s ? 'active' : ''}`}
              onClick={() => setFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Loans grid */}
      {isLoading ? (
        <div className="loans-grid">
          {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
        </div>
      ) : filtered.length === 0 ? (
        <EmptyState
          icon="💳"
          title={loans.length === 0 ? 'No loans added yet' : 'No matching loans'}
          description={loans.length === 0 ? 'Add your loans to track balances and get settlement strategies.' : 'Try a different filter or search term.'}
          actionLabel={loans.length === 0 ? 'Add Your First Loan' : undefined}
          onAction={loans.length === 0 ? openAdd : undefined}
        />
      ) : (
        <div className="loans-grid">
          {filtered.map((loan) => (
            <LoanCard key={loan.id} loan={loan} onEdit={openEdit} onDelete={openDelete} />
          ))}
        </div>
      )}

      {/* Add/Edit Modal */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editingLoan ? 'Edit Loan' : 'Add New Loan'}
        size="lg"
      >
        <form onSubmit={handleSubmit(onSubmit)} className="loan-form">
          <div className="loan-form-grid">
            <div className="form-group" style={{ gridColumn: '1 / -1' }}>
              <label className="form-label">Lender Name *</label>
              <input className={`form-input ${errors.lender_name ? 'error' : ''}`} placeholder="HDFC Bank" {...register('lender_name', { required: 'Lender name required' })} />
              {errors.lender_name && <span className="form-error">{errors.lender_name.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Loan Type *</label>
              <select className="form-select" {...register('loan_type', { required: true })}>
                {LOAN_TYPES.map((t) => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Status</label>
              <select className="form-select" {...register('status')}>
                {STATUSES.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Original Loan Amount (₹) *</label>
              <input type="number" className={`form-input ${errors.original_amount ? 'error' : ''}`} placeholder="500000" {...register('original_amount', { required: 'Required', min: 1 })} />
              {errors.original_amount && <span className="form-error">{errors.original_amount.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Outstanding Balance (₹) *</label>
              <input type="number" className={`form-input ${errors.outstanding_balance ? 'error' : ''}`} placeholder="350000" {...register('outstanding_balance', { required: 'Required', min: 0 })} />
              {errors.outstanding_balance && <span className="form-error">{errors.outstanding_balance.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label">Monthly EMI (₹)</label>
              <input type="number" className="form-input" placeholder="12000" {...register('emi_amount')} />
            </div>

            <div className="form-group">
              <label className="form-label">Interest Rate (% p.a.)</label>
              <input type="number" step="0.01" className="form-input" placeholder="14.5" {...register('interest_rate')} />
            </div>

            <div className="form-group">
              <label className="form-label">Overdue Months</label>
              <input type="number" className="form-input" placeholder="0" min="0" {...register('overdue_months')} />
            </div>

            <div className="form-group">
              <label className="form-label">Account Number</label>
              <input type="text" className="form-input" placeholder="XXXX-XXXX" {...register('account_number')} />
            </div>
          </div>

          <div className="loan-form-actions">
            <button type="button" className="btn btn-ghost" onClick={() => setModalOpen(false)}>Cancel</button>
            <button type="submit" className="btn btn-primary" disabled={isSaving}>
              {isSaving ? <><span className="spinner" /> Saving…</> : editingLoan ? 'Update Loan' : 'Add Loan'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirm Modal */}
      <Modal isOpen={deleteModal} onClose={() => setDeleteModal(false)} title="Delete Loan" size="sm">
        <div className="delete-confirm">
          <p className="delete-confirm-text">
            Are you sure you want to delete the loan from <strong>{deletingLoan?.lender_name}</strong>?
            This action cannot be undone.
          </p>
          <div className="delete-confirm-actions">
            <button className="btn btn-ghost" onClick={() => setDeleteModal(false)}>Cancel</button>
            <button className="btn btn-danger" onClick={handleDelete}>Delete Loan</button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
