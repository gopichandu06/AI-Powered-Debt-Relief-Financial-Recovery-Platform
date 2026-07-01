import { useState, useEffect } from 'react'
import { Copy, Download, FileText, Check, Clock } from 'lucide-react'
import toast from 'react-hot-toast'
import { loansAPI, lettersAPI } from '../../api/client'
import EmptyState from '../../components/ui/EmptyState'
import { SkeletonCard, SkeletonText } from '../../components/ui/LoadingSkeleton'
import './letters.css'

const TONES = [
  {
    value: 'professional',
    label: 'Professional',
    icon: '📋',
    desc: 'Formal tone for standard negotiation with clear, concise language',
  },
  {
    value: 'hardship',
    label: 'Hardship',
    icon: '🤝',
    desc: 'Empathetic tone explaining financial difficulties to request leniency',
  },
  {
    value: 'urgent',
    label: 'Urgent',
    icon: '⚡',
    desc: 'Time-sensitive tone for critical situations requiring immediate response',
  },
]

export default function Letters() {
  const [loans, setLoans] = useState([])
  const [selectedLoan, setSelectedLoan] = useState('')
  const [tone, setTone] = useState('professional')
  const [includeIncome, setIncludeIncome] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedLetter, setGeneratedLetter] = useState(null)
  const [pastLetters, setPastLetters] = useState([])
  const [copied, setCopied] = useState(false)
  const [loadingLoans, setLoadingLoans] = useState(true)
  const [loadingHistory, setLoadingHistory] = useState(true)

  useEffect(() => {
    loansAPI.list()
      .then((r) => {
        const loanList = r.data?.loans || r.data || []
        setLoans(loanList)
        if (loanList.length > 0) setSelectedLoan(loanList[0].id)
      })
      .catch(() => {})
      .finally(() => setLoadingLoans(false))

    lettersAPI.list({ limit: 5 })
      .then((r) => setPastLetters(r.data?.letters || r.data || []))
      .catch(() => {})
      .finally(() => setLoadingHistory(false))
  }, [])

  const handleGenerate = async () => {
    if (!selectedLoan) { toast.error('Please select a loan'); return }
    setIsGenerating(true)
    try {
      const res = await lettersAPI.generate({
        loan_id: selectedLoan,
        tone,
        include_income_details: includeIncome,
      })
      setGeneratedLetter(res.data)
      toast.success('Letter generated!')
      // refresh history
      lettersAPI.list({ limit: 5 })
        .then((r) => setPastLetters(r.data?.letters || r.data || []))
        .catch(() => {})
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate letter')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCopy = () => {
    const text = generatedLetter?.letter_content || generatedLetter?.content || ''
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      toast.success('Copied to clipboard!')
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const handleDownload = () => {
    const text = generatedLetter?.letter_content || generatedLetter?.content || ''
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `settlement-letter-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Letter downloaded!')
  }

  const selectedLoanObj = loans.find((l) => l.id === selectedLoan || String(l.id) === String(selectedLoan))

  return (
    <div className="page-container animate-fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">Letter Generator</h1>
          <p className="page-subtitle">Generate professional hardship and settlement letters</p>
        </div>
      </div>

      <div className="letters-layout">
        {/* ─── Left panel: Form ─── */}
        <div className="letters-form-panel">
          <div className="card">
            <h2 className="section-title">Generate Letter</h2>

            {/* Loan select */}
            <div className="form-group letters-form-group">
              <label className="form-label">Select Loan *</label>
              {loadingLoans ? (
                <div className="skeleton" style={{ height: '42px', borderRadius: '12px' }} />
              ) : loans.length === 0 ? (
                <p className="letters-no-loans">No loans added. <a href="/loans" style={{ color: 'var(--accent-primary)' }}>Add loans →</a></p>
              ) : (
                <select
                  className="form-select"
                  value={selectedLoan}
                  onChange={(e) => setSelectedLoan(e.target.value)}
                >
                  {loans.map((l) => (
                    <option key={l.id} value={l.id}>
                      {l.lender_name} — ₹{Number(l.outstanding_balance || 0).toLocaleString('en-IN')}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Tone selection */}
            <div className="letters-form-group">
              <label className="form-label">Letter Tone *</label>
              <div className="tone-options">
                {TONES.map((t) => (
                  <label key={t.value} className={`tone-option ${tone === t.value ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="tone"
                      value={t.value}
                      checked={tone === t.value}
                      onChange={(e) => setTone(e.target.value)}
                      className="tone-radio"
                    />
                    <span className="tone-icon">{t.icon}</span>
                    <div className="tone-info">
                      <strong>{t.label}</strong>
                      <span>{t.desc}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>

            {/* Include income toggle */}
            <div className="letters-form-group">
              <label className="letters-toggle-label">
                <div className="toggle-text">
                  <span className="form-label">Include Income Details</span>
                  <span className="form-label" style={{ color: 'var(--text-muted)', fontWeight: 'normal' }}>
                    Show income and expense information in the letter
                  </span>
                </div>
                <div
                  className={`toggle-switch ${includeIncome ? 'on' : 'off'}`}
                  onClick={() => setIncludeIncome((v) => !v)}
                  role="switch"
                  aria-checked={includeIncome}
                  tabIndex={0}
                >
                  <div className="toggle-thumb" />
                </div>
              </label>
            </div>

            <button
              className="btn btn-primary btn-lg letters-generate-btn"
              onClick={handleGenerate}
              disabled={isGenerating || !selectedLoan}
            >
              {isGenerating ? (
                <><span className="spinner" /> Generating with AI…</>
              ) : (
                <><FileText size={18} /> Generate Letter</>
              )}
            </button>
          </div>

          {/* Past letters */}
          <div className="card letters-history-card">
            <h3 className="section-title">Recent Letters</h3>
            {loadingHistory ? (
              <SkeletonText lines={3} />
            ) : pastLetters.length === 0 ? (
              <EmptyState icon="📝" title="No letters yet" description="Generate your first letter above." />
            ) : (
              <div className="letters-history-list">
                {pastLetters.map((letter, i) => (
                  <div key={letter.id || i} className="letter-history-item">
                    <div className="letter-history-icon">
                      <FileText size={14} />
                    </div>
                    <div className="letter-history-info">
                      <p className="letter-history-lender">{letter.lender_name || letter.loan?.lender_name || 'Letter'}</p>
                      <div className="letter-history-meta">
                        <span className="badge badge-muted" style={{ textTransform: 'capitalize' }}>{letter.tone || 'professional'}</span>
                        <span className="letter-history-date">
                          <Clock size={11} />
                          {new Date(letter.created_at || letter.timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })}
                        </span>
                      </div>
                    </div>
                    <button
                      className="btn btn-ghost btn-sm"
                      onClick={() => setGeneratedLetter(letter)}
                    >
                      View
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ─── Right panel: Preview ─── */}
        <div className="letters-preview-panel">
          {isGenerating ? (
            <div className="card letters-generating">
              <div className="letters-generating-content">
                <div className="spinner" style={{ width: 40, height: 40, borderWidth: 3 }} />
                <p>AI is crafting your personalized letter…</p>
                <SkeletonText lines={8} />
              </div>
            </div>
          ) : generatedLetter ? (
            <div className="card letters-letter-card">
              <div className="letters-letter-header">
                <div>
                  <h3 className="section-title" style={{ marginBottom: '4px' }}>Generated Letter</h3>
                  <span className="badge badge-success">Ready to use</span>
                </div>
                <div className="letters-letter-actions">
                  <button className="btn btn-secondary btn-sm" onClick={handleCopy}>
                    {copied ? <><Check size={14} /> Copied</> : <><Copy size={14} /> Copy</>}
                  </button>
                  <button className="btn btn-secondary btn-sm" onClick={handleDownload}>
                    <Download size={14} /> Download
                  </button>
                </div>
              </div>
              <div className="letter-paper">
                <pre className="letter-content">
                  {generatedLetter.letter_content || generatedLetter.content || 'Letter content not available.'}
                </pre>
              </div>
            </div>
          ) : (
            <div className="card letters-empty-preview">
              <EmptyState
                icon="📄"
                title="Letter preview"
                description="Select a loan, choose a tone, and click Generate Letter to create your personalized settlement letter."
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
