import type { Procedure, ProcedureListResponse } from '../api/procedures'
import { StatusBadge } from './StatusBadge'

interface Props {
  data: ProcedureListResponse
  onEdit: (p: Procedure) => void
  onDelete: (p: Procedure) => void
  page: number
  onPageChange: (page: number) => void
}

export function ProcedureTable({ data, onEdit, onDelete, page, onPageChange }: Props) {
  const totalPages = Math.ceil(data.total / data.page_size)

  return (
    <div className="animate-fade-in">
      <div className="border border-border bg-surface overflow-hidden" style={{ borderRadius: '2px' }}>
        <table className="w-full">
          <thead>
            <tr className="border-b-2 border-nav">
              <th className="px-5 py-3 text-left text-xs font-mono font-medium tracking-widest text-nav uppercase">
                Titolo
              </th>
              <th className="px-5 py-3 text-left text-xs font-mono font-medium tracking-widest text-nav uppercase w-36">
                Categoria
              </th>
              <th className="px-5 py-3 text-left text-xs font-mono font-medium tracking-widest text-nav uppercase w-32">
                Autore
              </th>
              <th className="px-5 py-3 text-left text-xs font-mono font-medium tracking-widest text-nav uppercase w-28">
                Aggiornato
              </th>
              <th className="px-5 py-3 text-left text-xs font-mono font-medium tracking-widest text-nav uppercase w-28">
                Stato
              </th>
              <th className="w-16" />
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {data.items.length === 0 && (
              <tr>
                <td colSpan={6} className="px-5 py-12 text-center text-muted text-sm font-light">
                  Nessuna procedura trovata. Aggiungine una con il pulsante in alto.
                </td>
              </tr>
            )}
            {data.items.map((proc, i) => (
              <tr
                key={proc.id}
                onClick={() => onEdit(proc)}
                className="group cursor-pointer hover:bg-accent-light transition-colors duration-150"
                style={{
                  animationDelay: `${i * 40}ms`,
                  borderLeft: '3px solid transparent',
                }}
                onMouseEnter={(e) => {
                  (e.currentTarget as HTMLElement).style.borderLeft = '3px solid #B5492C'
                }}
                onMouseLeave={(e) => {
                  (e.currentTarget as HTMLElement).style.borderLeft = '3px solid transparent'
                }}
              >
                <td className="px-5 py-3.5">
                  <span className="text-sm font-medium text-gray-900 group-hover:text-accent transition-colors">
                    {proc.titolo}
                  </span>
                  {proc.tags.length > 0 && (
                    <div className="mt-0.5 flex gap-1 flex-wrap">
                      {proc.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="text-xs text-muted font-mono">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </td>
                <td className="px-5 py-3.5 text-sm text-muted">
                  {proc.categoria ?? <span className="text-border">—</span>}
                </td>
                <td className="px-5 py-3.5 text-sm text-muted">
                  {proc.autore ?? <span className="text-border">—</span>}
                </td>
                <td className="px-5 py-3.5 text-sm text-muted font-mono">
                  {new Date(proc.updated_at).toLocaleDateString('it-IT', {
                    day: '2-digit',
                    month: '2-digit',
                    year: '2-digit',
                  })}
                </td>
                <td className="px-5 py-3.5">
                  <StatusBadge status={proc.compilation_status} />
                  {proc.compilation_status === 'failed' && proc.compilation_error && (
                    <p className="text-xs text-accent mt-1 max-w-xs truncate font-mono">
                      {proc.compilation_error}
                    </p>
                  )}
                </td>
                <td className="px-5 py-3.5 text-right">
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      onDelete(proc)
                    }}
                    className="opacity-0 group-hover:opacity-100 text-xs text-muted hover:text-accent transition-all duration-150 font-mono tracking-wide"
                  >
                    elimina
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between text-sm text-muted">
          <span className="font-mono text-xs">
            {data.total} procedure · pagina {page}/{totalPages}
          </span>
          <div className="flex gap-2">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="px-3 py-1.5 border border-border text-xs font-mono hover:border-accent hover:text-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              style={{ borderRadius: '2px' }}
            >
              ← prec
            </button>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="px-3 py-1.5 border border-border text-xs font-mono hover:border-accent hover:text-accent disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              style={{ borderRadius: '2px' }}
            >
              succ →
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
