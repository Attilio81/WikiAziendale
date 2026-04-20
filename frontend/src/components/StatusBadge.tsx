const STYLES: Record<string, string> = {
  pending: 'bg-amber-50 text-amber-700 border-amber-200 animate-pulse',
  compiled: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  failed: 'bg-red-50 text-accent border-red-200',
}

const LABELS: Record<string, string> = {
  pending: 'in attesa',
  compiled: 'compilato',
  failed: 'errore',
}

export function StatusBadge({ status }: { status: string }) {
  const style = STYLES[status] ?? 'bg-gray-50 text-gray-600 border-gray-200'
  const label = LABELS[status] ?? status
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 border font-mono text-xs tracking-wide ${style}`}
      style={{ borderRadius: '2px' }}
    >
      {label}
    </span>
  )
}
