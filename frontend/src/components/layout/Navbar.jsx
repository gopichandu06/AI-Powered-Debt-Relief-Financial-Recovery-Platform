import { useState, useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'
import { Bell, Menu, ChevronDown, User, LogOut, Settings } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'
import './navbar.css'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/profile': 'Profile',
  '/loans': 'My Loans',
  '/analysis': 'Financial Analysis',
  '/settlement': 'Debt Settlement',
  '/letters': 'Letter Generator',
  '/history': 'History',
  '/rights': 'Borrower Rights',
}

function useCurrentTime() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60000)
    return () => clearInterval(id)
  }, [])
  return now
}

export default function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth()
  const location = useLocation()
  const now = useCurrentTime()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  const pageTitle = pageTitles[location.pathname] || 'FinRelief AI'

  const initials = user?.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    : user?.email?.slice(0, 2).toUpperCase() || 'U'

  const formatted = now.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })

  useEffect(() => {
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  return (
    <header className="navbar">
      <div className="navbar-left">
        <button className="navbar-hamburger" onClick={onMenuClick} aria-label="Open menu">
          <Menu size={20} />
        </button>
        <div className="navbar-page-info">
          <h1 className="navbar-title">{pageTitle}</h1>
          <span className="navbar-date">{formatted}</span>
        </div>
      </div>

      <div className="navbar-right">
        <button className="navbar-icon-btn" aria-label="Notifications">
          <Bell size={18} />
          <span className="navbar-notification-dot" />
        </button>

        <div className="navbar-user-menu" ref={dropdownRef}>
          <button
            className="navbar-user-btn"
            onClick={() => setDropdownOpen((o) => !o)}
          >
            <div className="navbar-avatar">{initials}</div>
            <span className="navbar-user-name">{user?.full_name?.split(' ')[0] || 'User'}</span>
            <ChevronDown
              size={14}
              className={`navbar-chevron ${dropdownOpen ? 'open' : ''}`}
            />
          </button>

          {dropdownOpen && (
            <div className="navbar-dropdown animate-slide-down">
              <div className="navbar-dropdown-header">
                <div className="navbar-dropdown-avatar">{initials}</div>
                <div>
                  <p className="navbar-dropdown-name">{user?.full_name || 'User'}</p>
                  <p className="navbar-dropdown-email">{user?.email}</p>
                </div>
              </div>
              <div className="navbar-dropdown-divider" />
              <a href="/profile" className="navbar-dropdown-item" onClick={() => setDropdownOpen(false)}>
                <User size={14} />
                Profile Settings
              </a>
              <button className="navbar-dropdown-item danger" onClick={logout}>
                <LogOut size={14} />
                Sign Out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
