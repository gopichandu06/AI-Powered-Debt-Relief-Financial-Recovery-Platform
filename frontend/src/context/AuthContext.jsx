import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { authAPI } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  const isAuthenticated = Boolean(token && user)

  // ─── Validate existing session on mount ───
  useEffect(() => {
    const storedToken = localStorage.getItem('finrelief_token')
    if (storedToken) {
      setToken(storedToken)
      authAPI
        .getMe()
        .then((res) => {
          setUser(res.data)
        })
        .catch(() => {
          localStorage.removeItem('finrelief_token')
          localStorage.removeItem('finrelief_user')
          setToken(null)
          setUser(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

  const login = useCallback(async (email, password) => {
    const res = await authAPI.login({ email, password })
    const { access_token } = res.data
    localStorage.setItem('finrelief_token', access_token)
    
    const meRes = await authAPI.getMe()
    const userData = meRes.data
    
    localStorage.setItem('finrelief_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    navigate('/dashboard')
    return res.data
  }, [navigate])

  const register = useCallback(async (data) => {
    const res = await authAPI.register(data)
    const { access_token } = res.data
    localStorage.setItem('finrelief_token', access_token)
    
    const meRes = await authAPI.getMe()
    const userData = meRes.data
    
    localStorage.setItem('finrelief_user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
    navigate('/dashboard')
    return res.data
  }, [navigate])

  const logout = useCallback(() => {
    localStorage.removeItem('finrelief_token')
    localStorage.removeItem('finrelief_user')
    setToken(null)
    setUser(null)
    navigate('/login')
  }, [navigate])

  const updateUser = useCallback((userData) => {
    setUser((prev) => ({ ...prev, ...userData }))
    localStorage.setItem('finrelief_user', JSON.stringify({ ...user, ...userData }))
  }, [user])

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export default AuthContext
