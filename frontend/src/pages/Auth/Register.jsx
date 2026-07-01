import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import './auth.css'

function getPasswordStrength(password) {
  if (!password) return { level: 0, label: '', color: '' }
  let score = 0
  if (password.length >= 8) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++
  const map = [
    { label: 'Too weak', color: '#ef4444' },
    { label: 'Weak', color: '#f59e0b' },
    { label: 'Fair', color: '#f59e0b' },
    { label: 'Good', color: '#10b981' },
    { label: 'Strong', color: '#10b981' },
  ]
  return { level: score, ...map[score] }
}

export default function Register() {
  const { register: registerUser, isAuthenticated } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [passwordVal, setPasswordVal] = useState('')

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm()

  const password = watch('password', '')
  const strength = getPasswordStrength(password)

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  const onSubmit = async (data) => {
    if (data.password !== data.confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    setIsLoading(true)
    try {
      await registerUser({
        full_name: data.fullName,
        email: data.email,
        password: data.password,
      })
      toast.success('Account created! Welcome to FinRelief AI 🎉')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Registration failed. Try again.'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      {/* Left brand panel */}
      <div className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">
            <span className="auth-logo-icon">💰</span>
            <span className="auth-logo-text">FinRelief AI</span>
          </div>
          <div className="auth-brand-hero">
            <h1 className="auth-brand-title">
              Start Your Journey to Debt Freedom
            </h1>
            <p className="auth-brand-subtitle">
              Join thousands who've used AI-powered tools to negotiate debt settlements
              and rebuild their financial health.
            </p>
          </div>
          <div className="auth-stats">
            <div className="auth-stat">
              <span className="auth-stat-value">₹2.4Cr+</span>
              <span className="auth-stat-label">Debt settled</span>
            </div>
            <div className="auth-stat">
              <span className="auth-stat-value">4,800+</span>
              <span className="auth-stat-label">Users helped</span>
            </div>
            <div className="auth-stat">
              <span className="auth-stat-value">38%</span>
              <span className="auth-stat-label">Avg. savings</span>
            </div>
          </div>
        </div>
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
        <div className="auth-orb auth-orb-3" />
      </div>

      {/* Right form panel */}
      <div className="auth-form-panel">
        <div className="auth-form-card animate-slide-up">
          <div className="auth-form-header">
            <h2 className="auth-form-title">Create your account</h2>
            <p className="auth-form-subtitle">Free forever. No credit card required.</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div className="form-group">
              <label className="form-label" htmlFor="fullName">Full Name</label>
              <input
                id="fullName"
                type="text"
                className={`form-input ${errors.fullName ? 'error' : ''}`}
                placeholder="Rajesh Kumar"
                autoComplete="name"
                {...register('fullName', { required: 'Full name is required' })}
              />
              {errors.fullName && <span className="form-error">{errors.fullName.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="email">Email address</label>
              <input
                id="email"
                type="email"
                className={`form-input ${errors.email ? 'error' : ''}`}
                placeholder="you@example.com"
                autoComplete="email"
                {...register('email', {
                  required: 'Email is required',
                  pattern: { value: /^\S+@\S+\.\S+$/, message: 'Invalid email' },
                })}
              />
              {errors.email && <span className="form-error">{errors.email.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="reg-password">Password</label>
              <div className="auth-input-wrapper">
                <input
                  id="reg-password"
                  type={showPassword ? 'text' : 'password'}
                  className={`form-input auth-password-input ${errors.password ? 'error' : ''}`}
                  placeholder="At least 8 characters"
                  autoComplete="new-password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 6, message: 'Minimum 6 characters' },
                  })}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword((s) => !s)}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {password && (
                <div className="password-strength">
                  <div className="strength-bars">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className="strength-bar"
                        style={{
                          background: i <= strength.level ? strength.color : 'var(--bg-tertiary)',
                          transition: 'background 0.3s ease',
                        }}
                      />
                    ))}
                  </div>
                  <span className="strength-label" style={{ color: strength.color }}>
                    {strength.label}
                  </span>
                </div>
              )}
              {errors.password && <span className="form-error">{errors.password.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
              <div className="auth-input-wrapper">
                <input
                  id="confirmPassword"
                  type={showConfirm ? 'text' : 'password'}
                  className={`form-input auth-password-input ${errors.confirmPassword ? 'error' : ''}`}
                  placeholder="Repeat your password"
                  autoComplete="new-password"
                  {...register('confirmPassword', {
                    required: 'Please confirm your password',
                    validate: (val) => val === password || 'Passwords do not match',
                  })}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowConfirm((s) => !s)}
                >
                  {showConfirm ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.confirmPassword && (
                <span className="form-error">{errors.confirmPassword.message}</span>
              )}
            </div>

            <label className="auth-checkbox-label auth-terms">
              <input
                type="checkbox"
                className="auth-checkbox"
                {...register('terms', { required: 'You must accept terms' })}
              />
              <span>
                I agree to the{' '}
                <a href="#" className="auth-link">Terms of Service</a>
                {' '}and{' '}
                <a href="#" className="auth-link">Privacy Policy</a>
              </span>
            </label>
            {errors.terms && <span className="form-error">{errors.terms.message}</span>}

            <button
              type="submit"
              className="btn btn-primary btn-lg auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner" />
                  Creating account…
                </>
              ) : (
                'Create Free Account'
              )}
            </button>
          </form>

          <div className="auth-form-footer">
            Already have an account?{' '}
            <Link to="/login" className="auth-link">Sign in →</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
