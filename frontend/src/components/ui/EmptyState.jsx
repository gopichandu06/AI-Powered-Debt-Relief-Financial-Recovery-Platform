export default function EmptyState({ icon = '📭', title, description, actionLabel, onAction }) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '64px 32px',
        textAlign: 'center',
        gap: '16px',
      }}
    >
      <div style={{ fontSize: '3.5rem', lineHeight: 1, filter: 'grayscale(0.3)' }}>{icon}</div>
      {title && (
        <h3
          style={{
            fontSize: 'var(--font-xl)',
            fontWeight: '600',
            color: 'var(--text-primary)',
          }}
        >
          {title}
        </h3>
      )}
      {description && (
        <p
          style={{
            fontSize: 'var(--font-sm)',
            color: 'var(--text-muted)',
            maxWidth: '360px',
            lineHeight: 1.6,
          }}
        >
          {description}
        </p>
      )}
      {actionLabel && onAction && (
        <button className="btn btn-primary" onClick={onAction} style={{ marginTop: '8px' }}>
          {actionLabel}
        </button>
      )}
    </div>
  )
}
