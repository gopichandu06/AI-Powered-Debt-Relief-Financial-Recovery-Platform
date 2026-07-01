import { useState } from 'react'
import { Link, Navigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { Eye, EyeOff, CheckCircle, Shield, TrendingUp, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuth } from '../../context/AuthContext'
import './auth.css'

const features = [
  { icon: TrendingUp, text: 'AI-powered financial health analysis' },
  { icon: Shield, text: 'Debt settlement negotiation strategies' },
  { icon: FileText, text: 'Professional hardship letter generation' },
  { icon: CheckCircle, text: 'Know your rights as a borrower' },
]

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm()

  if (isAuthenticated) return <Navigate to="/dashboard" replace />

  const onSubmit = async (data) => {
    setIsLoading(true)
    try {
      await login(data.email, data.password)
      toast.success('Welcome back!')
    } catch (err) {
      const msg = err.response?.data?.detail || 'Invalid email or password'
      toast.error(msg)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-container">
      {/* Left panel */}
      <div className="auth-brand-panel">
        <div className="auth-brand-content">
          <div className="auth-logo">
            <span className="auth-logo-icon">💰</span>
            <span className="auth-logo-text">FinRelief AI</span>
          </div>
          <div className="auth-brand-hero">
            <h1 className="auth-brand-title">
              Take Control of Your Financial Future
            </h1>
            <p className="auth-brand-subtitle">
              AI-powered debt relief platform that helps you negotiate settlements,
              analyze your financial health, and recover faster.
            </p>
          </div>
          <ul className="auth-features-list">
            {features.map(({ icon: Icon, text }) => (
              <li key={text} className="auth-feature-item">
                <span className="auth-feature-icon">
                  <Icon size={16} />
                </span>
                <span>{text}</span>
              </li>
            ))}
          </ul>
          <div className="auth-brand-footer">
            Trusted by thousands of borrowers across India
          </div>
        </div>
        {/* Decorative orbs */}
        <div className="auth-orb auth-orb-1" />
        <div className="auth-orb auth-orb-2" />
        <div className="auth-orb auth-orb-3" />
      </div>

      {/* Right form panel */}
      <div className="auth-form-panel">
        <div className="auth-form-card animate-slide-up">
          <div className="auth-form-header">
            <h2 className="auth-form-title">Welcome back</h2>
            <p className="auth-form-subtitle">Sign in to your account to continue</p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit(onSubmit)} noValidate>
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
                  pattern: { value: /^\S+@\S+\.\S+$/, message: 'Invalid email address' },
                })}
              />
              {errors.email && <span className="form-error">{errors.email.message}</span>}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="password">Password</label>
              <div className="auth-input-wrapper">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  className={`form-input auth-password-input ${errors.password ? 'error' : ''}`}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  {...register('password', {
                    required: 'Password is required',
                    minLength: { value: 6, message: 'Password must be at least 6 characters' },
                  })}
                />
                <button
                  type="button"
                  className="auth-password-toggle"
                  onClick={() => setShowPassword((s) => !s)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              {errors.password && <span className="form-error">{errors.password.message}</span>}
            </div>

            <div className="auth-form-options">
              <label className="auth-checkbox-label">
                <input type="checkbox" className="auth-checkbox" />
                <span>Remember me</span>
              </label>
              <a href="#" className="auth-forgot-link">Forgot password?</a>
            </div>

            <button
              type="submit"
              className="btn btn-primary btn-lg auth-submit-btn"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner" />
                  Signing in…
                </>
              ) : (
                'Sign in to FinRelief AI'
              )}
            </button>
          </form>

          <div className="auth-form-footer">
            Don't have an account?{' '}
            <Link to="/register" className="auth-link">Create account →</Link>
          </div>
        </div>
      </div>
    </div>
  )
}
