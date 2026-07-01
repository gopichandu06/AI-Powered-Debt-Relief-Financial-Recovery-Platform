import { useState, useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { Save, User, DollarSign, Briefcase, MapPin, Star } from 'lucide-react'
import toast from 'react-hot-toast'
import { profileAPI } from '../../api/client'
import { useAuth } from '../../context/AuthContext'
import './profile.css'

const EMPLOYMENT_TYPES = [
  { value: 'salaried', label: 'Salaried Employee' },
  { value: 'self_employed', label: 'Self Employed' },
  { value: 'business', label: 'Business Owner' },
  { value: 'freelancer', label: 'Freelancer' },
  { value: 'unemployed', label: 'Unemployed' },
  { value: 'retired', label: 'Retired' },
]

function getCreditScoreLabel(score) {
  if (score >= 750) return { label: 'Excellent', color: '#10b981' }
  if (score >= 700) return { label: 'Good', color: '#6366f1' }
  if (score >= 650) return { label: 'Fair', color: '#f59e0b' }
  if (score >= 600) return { label: 'Poor', color: '#f59e0b' }
  return { label: 'Very Poor', color: '#ef4444' }
}

export default function Profile() {
  const { user, updateUser } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const [creditScore, setCreditScore] = useState(650)

  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm({
    defaultValues: {
      full_name: '',
      monthly_income: '',
      monthly_expenses: '',
      employment_type: 'salaried',
      credit_score: 650,
      dependents: 0,
      city: '',
      state: '',
    },
  })

  const watchedScore = watch('credit_score', 650)
  const scoreInfo = getCreditScoreLabel(Number(watchedScore))

  useEffect(() => {
    profileAPI.get()
      .then((r) => {
        const data = r.data
        Object.entries(data).forEach(([k, v]) => setValue(k, v ?? ''))
        setCreditScore(data.credit_score || 650)
      })
      .catch(() => {
        // Pre-fill from auth user if profile fetch fails
        if (user?.full_name) setValue('full_name', user.full_name)
      })
      .finally(() => setIsFetching(false))
  }, [])

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      const payload = {
        ...data,
        monthly_income: Number(data.monthly_income),
        monthly_expenses: Number(data.monthly_expenses),
        credit_score: Number(data.credit_score),
        dependents: Number(data.dependents),
      }
      const res = await profileAPI.update(payload)
      updateUser({ full_name: data.full_name })
      toast.success('Profile updated successfully!')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile')
    } finally {
      setIsLoading(false)
    }
  }

  if (isFetching) {
    return (
      <div className="page-container">
        <div className="profile-skeleton">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div className="skeleton" style={{ height: '14px', width: '40%' }} />
              <div className="skeleton" style={{ height: '42px' }} />
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Profile Settings</h1>
          <p className="page-subtitle">Update your financial profile for accurate analysis</p>
        </div>
      </div>

      <div className="profile-layout">
        {/* Profile summary card */}
        <div className="profile-sidebar">
          <div className="card profile-summary-card">
            <div className="profile-avatar-lg">
              {user?.full_name?.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2) || 'U'}
            </div>
            <h3 className="profile-summary-name">{user?.full_name || 'Your Name'}</h3>
            <p className="profile-summary-email">{user?.email}</p>
            <div className="profile-summary-divider" />
            <div className="profile-credit-display">
              <span className="profile-credit-label">Credit Score</span>
              <span className="profile-credit-value" style={{ color: scoreInfo.color }}>
                {watchedScore}
              </span>
              <span className="profile-credit-tag" style={{ color: scoreInfo.color }}>
                {scoreInfo.label}
              </span>
            </div>
            <div className="profile-score-bar-track">
              <div
                className="profile-score-bar-fill"
                style={{
                  width: `${((watchedScore - 300) / 550) * 100}%`,
                  background: scoreInfo.color,
                }}
              />
            </div>
            <div className="profile-score-range">
              <span>300</span>
              <span>850</span>
            </div>
          </div>
        </div>

        {/* Form */}
        <form className="profile-form" onSubmit={handleSubmit(onSubmit)}>
          {/* Personal Info */}
          <div className="card profile-section">
            <div className="profile-section-header">
              <User size={18} className="profile-section-icon" />
              <h2 className="profile-section-title">Personal Information</h2>
            </div>
            <div className="profile-fields-grid">
              <div className="form-group" style={{ gridColumn: '1 / -1' }}>
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className={`form-input ${errors.full_name ? 'error' : ''}`}
                  placeholder="Your full name"
                  {...register('full_name', { required: 'Full name is required' })}
                />
                {errors.full_name && <span className="form-error">{errors.full_name.message}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">City</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Mumbai"
                  {...register('city')}
                />
              </div>
              <div className="form-group">
                <label className="form-label">State</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="Maharashtra"
                  {...register('state')}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Dependents</label>
                <input
                  type="number"
                  className="form-input"
                  placeholder="0"
                  min="0"
                  max="20"
                  {...register('dependents')}
                />
              </div>
            </div>
          </div>

          {/* Financial Info */}
          <div className="card profile-section">
            <div className="profile-section-header">
              <DollarSign size={18} className="profile-section-icon" />
              <h2 className="profile-section-title">Financial Details</h2>
            </div>
            <div className="profile-fields-grid">
              <div className="form-group">
                <label className="form-label">Monthly Income (₹)</label>
                <input
                  type="number"
                  className={`form-input ${errors.monthly_income ? 'error' : ''}`}
                  placeholder="75000"
                  {...register('monthly_income', {
                    required: 'Monthly income is required',
                    min: { value: 1, message: 'Must be positive' },
                  })}
                />
                {errors.monthly_income && <span className="form-error">{errors.monthly_income.message}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">Monthly Expenses (₹)</label>
                <input
                  type="number"
                  className={`form-input ${errors.monthly_expenses ? 'error' : ''}`}
                  placeholder="35000"
                  {...register('monthly_expenses', {
                    required: 'Monthly expenses required',
                    min: { value: 0, message: 'Cannot be negative' },
                  })}
                />
                {errors.monthly_expenses && <span className="form-error">{errors.monthly_expenses.message}</span>}
              </div>
              <div className="form-group">
                <label className="form-label">Employment Type</label>
                <select className="form-select" {...register('employment_type')}>
                  {EMPLOYMENT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Credit Score */}
          <div className="card profile-section">
            <div className="profile-section-header">
              <Star size={18} className="profile-section-icon" />
              <h2 className="profile-section-title">Credit Score</h2>
            </div>
            <div className="form-group">
              <label className="form-label">
                Credit Score: <strong style={{ color: scoreInfo.color }}>{watchedScore} — {scoreInfo.label}</strong>
              </label>
              <input
                type="range"
                min="300"
                max="850"
                step="1"
                className="profile-slider"
                {...register('credit_score')}
                style={{ '--slider-color': scoreInfo.color }}
              />
              <div className="profile-slider-labels">
                <span>300 (Very Poor)</span>
                <span>550 (Fair)</span>
                <span>750 (Excellent)</span>
                <span>850</span>
              </div>
            </div>
          </div>

          <div className="profile-form-actions">
            <button type="submit" className="btn btn-primary btn-lg" disabled={isLoading}>
              {isLoading ? (
                <><span className="spinner" /> Saving…</>
              ) : (
                <><Save size={16} /> Save Profile</>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
