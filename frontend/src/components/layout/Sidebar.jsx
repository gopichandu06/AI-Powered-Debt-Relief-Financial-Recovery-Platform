import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  User,
  CreditCard,
  BarChart3,
  Target,
  FileText,
  Clock,
  Shield,
  LogOut,
  X,
  ChevronRight,
} from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import './sidebar.css'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/profile', icon: User, label: 'Profile' },
  { to: '/loans', icon: CreditCard, label: 'My Loans' },
  { to: '/analysis', icon: BarChart3, label: 'Analysis' },
  { to: '/settlement', icon: Target, label: 'Settlement' },
  { to: '/letters', icon: FileText, label: 'Letters' },
  { to: '/history', icon: Clock, label: 'History' },
  { to: '/rights', icon: Shield, label: 'Borrower Rights' },
]

export default function Sidebar({ isOpen, onClose }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() || 'U'

  const handleLogout = () => {
    logout()
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="sidebar-overlay" onClick={onClose} />
      )}

      <aside className={`sidebar ${isOpen ? 'sidebar-open' : ''}`}>
        {/* Logo */}
        <div className="sidebar-logo">
          <span className="sidebar-logo-icon">💰</span>
          <span className="sidebar-logo-text">FinRelief AI</span>
          <button className="sidebar-close-btn" onClick={onClose}>
            <X size={18} />
          </button>
        </div>

        {/* Nav */}
        <nav className="sidebar-nav">
          <div className="sidebar-nav-group">
            <span className="sidebar-nav-label">Menu</span>
            {navItems.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `sidebar-nav-item ${isActive ? 'active' : ''}`
                }
                onClick={onClose}
              >
                <span className="sidebar-nav-icon">
                  <Icon size={18} />
                </span>
                <span className="sidebar-nav-text">{label}</span>
                <ChevronRight size={14} className="sidebar-nav-arrow" />
              </NavLink>
            ))}
          </div>
        </nav>

        {/* User section */}
        <div className="sidebar-user">
          <div className="sidebar-user-info">
            <div className="sidebar-avatar">{initials}</div>
            <div className="sidebar-user-details">
              <span className="sidebar-user-name">
                {user?.full_name || 'User'}
              </span>
              <span className="sidebar-user-email">{user?.email || ''}</span>
            </div>
          </div>
          <button className="sidebar-logout-btn" onClick={handleLogout}>
            <LogOut size={16} />
            <span>Logout</span>
          </button>
        </div>
      </aside>
    </>
  )
}
