import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// ─── Request interceptor ───
client.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('finrelief_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ─── Response interceptor ───
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('finrelief_token')
      localStorage.removeItem('finrelief_user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ─── Auth API ───
export const authAPI = {
  register: (data) => client.post('/api/auth/register', data),
  login: (data) => {
    const params = new URLSearchParams()
    params.append('username', data.email)
    params.append('password', data.password)
    return client.post('/api/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    })
  },
  getMe: () => client.get('/api/auth/me'),
}

// ─── Profile API ───
export const profileAPI = {
  get: () => client.get('/api/profile'),
  update: (data) => client.put('/api/profile', data),
}

// ─── Loans API ───
export const loansAPI = {
  list: (params) => client.get('/api/loans', { params }),
  create: (data) => client.post('/api/loans', data),
  get: (id) => client.get(`/api/loans/${id}`),
  update: (id, data) => client.put(`/api/loans/${id}`, data),
  delete: (id) => client.delete(`/api/loans/${id}`),
}

// ─── Analysis API ───
export const analysisAPI = {
  getFinancialHealth: () => client.get('/api/analysis/financial-health'),
  getDebtSummary: () => client.get('/api/analysis/debt-summary'),
}

// ─── Settlement API ───
export const settlementAPI = {
  calculate: () => client.post('/api/settlement/calculate'),
  getAIAdvice: (data) => client.post('/api/settlement/ai-advice', data),
  getHistory: (params) => client.get('/api/settlement/history', { params }),
}

// ─── Letters API ───
export const lettersAPI = {
  generate: (data) => client.post('/api/letters/generate', data),
  list: (params) => client.get('/api/letters', { params }),
  get: (id) => client.get(`/api/letters/${id}`),
}

// ─── History API ───
export const historyAPI = {
  getSettlements: (params) => client.get('/api/history/settlements', { params }),
  getLetters: (params) => client.get('/api/history/letters', { params }),
  getActivity: (params) => client.get('/api/history/activity', { params }),
  getSummary: () => client.get('/api/history/summary'),
}

export default client
