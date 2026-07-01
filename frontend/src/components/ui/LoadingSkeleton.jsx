export function SkeletonCard() {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div className="skeleton" style={{ height: '16px', width: '40%' }} />
      <div className="skeleton" style={{ height: '36px', width: '65%' }} />
      <div className="skeleton" style={{ height: '12px', width: '90%' }} />
      <div className="skeleton" style={{ height: '12px', width: '70%' }} />
      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
        <div className="skeleton" style={{ height: '32px', flex: 1 }} />
        <div className="skeleton" style={{ height: '32px', flex: 1 }} />
      </div>
    </div>
  )
}

export function SkeletonMetric() {
  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div className="skeleton" style={{ height: '14px', width: '50%' }} />
        <div className="skeleton skeleton-circle" style={{ width: '36px', height: '36px' }} />
      </div>
      <div className="skeleton" style={{ height: '40px', width: '70%' }} />
      <div className="skeleton" style={{ height: '12px', width: '40%' }} />
    </div>
  )
}

export function SkeletonTable({ rows = 5 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr 1fr 1fr 120px',
            gap: '16px',
            padding: '12px 16px',
            background: 'var(--bg-secondary)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
          }}
        >
          <div className="skeleton" style={{ height: '14px' }} />
          <div className="skeleton" style={{ height: '14px' }} />
          <div className="skeleton" style={{ height: '14px' }} />
          <div className="skeleton" style={{ height: '14px' }} />
          <div className="skeleton" style={{ height: '14px' }} />
        </div>
      ))}
    </div>
  )
}

export function SkeletonText({ lines = 3 }) {
  const widths = ['90%', '75%', '55%']
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="skeleton"
          style={{ height: '14px', width: widths[i % widths.length] }}
        />
      ))}
    </div>
  )
}

export default function LoadingSkeleton({ type = 'card', count = 1, ...props }) {
  const Component = {
    card: SkeletonCard,
    metric: SkeletonMetric,
    table: SkeletonTable,
    text: SkeletonText,
  }[type] || SkeletonCard

  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <Component key={i} {...props} />
      ))}
    </>
  )
}
