import { useState, useEffect, type FormEvent } from 'react'
import type { Procedure, ProcedureCreate } from '../api/procedures'

interface Props {
  procedure: Procedure | null
  onSave: (data: ProcedureCreate) => Promise<void>
  onClose: () => void
}

export function ProcedureModal({ procedure, onSave, onClose }: Props) {
  const [titolo, setTitolo] = useState('')
  const [categoria, setCategoria] = useState('')
  const [contenuto, setContenuto] = useState('')
  const [autore, setAutore] = useState('')
  const [tagsInput, setTagsInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (procedure) {
      setTitolo(procedure.titolo)
      setCategoria(procedure.categoria ?? '')
      setContenuto(procedure.contenuto_md)
      setAutore(procedure.autore ?? '')
      setTagsInput(procedure.tags.join(', '))
    } else {
      setTitolo(''); setCategoria(''); setContenuto(''); setAutore(''); setTagsInput('')
    }
    setError(null)
  }, [procedure])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      await onSave({
        titolo: titolo.trim(),
        categoria: categoria.trim() || undefined,
        contenuto_md: contenuto,
        autore: autore.trim() || undefined,
        tags: tagsInput.split(',').map((t) => t.trim()).filter(Boolean),
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Errore durante il salvataggio')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-nav/60 backdrop-blur-sm"
        onClick={onClose}
      />

      {/* Panel */}
      <div
        className="relative bg-surface w-full max-w-2xl shadow-2xl animate-slide-up flex flex-col max-h-[90vh]"
        style={{ borderRadius: '2px' }}
      >
        {/* Header */}
        <div className="bg-nav px-6 py-4 flex items-center justify-between flex-shrink-0">
          <h2 className="font-display text-lg font-light text-white tracking-wide">
            {procedure ? 'Modifica procedura' : 'Nuova procedura'}
          </h2>
          <button
            onClick={onClose}
            className="text-white/50 hover:text-white transition-colors text-2xl leading-none font-light"
            aria-label="Chiudi"
          >
            ×
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col flex-1 overflow-hidden">
          <div className="overflow-y-auto flex-1 px-6 py-5 space-y-4">
            {/* Titolo */}
            <div>
              <label className="block text-xs font-mono tracking-widest text-muted uppercase mb-1.5">
                Titolo <span className="text-accent">*</span>
              </label>
              <input
                required
                value={titolo}
                onChange={(e) => setTitolo(e.target.value)}
                className="w-full border border-border px-3 py-2 text-sm bg-bg focus:outline-none focus:border-nav transition-colors"
                style={{ borderRadius: '2px' }}
                placeholder="Es. Gestione DDT fornitore"
              />
            </div>

            {/* Categoria + Autore */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono tracking-widest text-muted uppercase mb-1.5">
                  Categoria
                </label>
                <input
                  value={categoria}
                  onChange={(e) => setCategoria(e.target.value)}
                  className="w-full border border-border px-3 py-2 text-sm bg-bg focus:outline-none focus:border-nav transition-colors"
                  style={{ borderRadius: '2px' }}
                  placeholder="Es. Magazzino"
                />
              </div>
              <div>
                <label className="block text-xs font-mono tracking-widest text-muted uppercase mb-1.5">
                  Autore
                </label>
                <input
                  value={autore}
                  onChange={(e) => setAutore(e.target.value)}
                  className="w-full border border-border px-3 py-2 text-sm bg-bg focus:outline-none focus:border-nav transition-colors"
                  style={{ borderRadius: '2px' }}
                  placeholder="Es. Mario Rossi"
                />
              </div>
            </div>

            {/* Contenuto */}
            <div>
              <label className="block text-xs font-mono tracking-widest text-muted uppercase mb-1.5">
                Contenuto (Markdown) <span className="text-accent">*</span>
              </label>
              <textarea
                required
                value={contenuto}
                onChange={(e) => setContenuto(e.target.value)}
                rows={12}
                className="w-full border border-border px-3 py-2 text-sm font-mono bg-bg focus:outline-none focus:border-nav transition-colors resize-none leading-relaxed"
                style={{ borderRadius: '2px' }}
                placeholder={'## Descrizione\n\nScrivi qui la procedura in markdown...'}
              />
            </div>

            {/* Tag */}
            <div>
              <label className="block text-xs font-mono tracking-widest text-muted uppercase mb-1.5">
                Tag (separati da virgola)
              </label>
              <input
                value={tagsInput}
                onChange={(e) => setTagsInput(e.target.value)}
                className="w-full border border-border px-3 py-2 text-sm font-mono bg-bg focus:outline-none focus:border-nav transition-colors"
                style={{ borderRadius: '2px' }}
                placeholder="magazzino, DDT, ricezione"
              />
            </div>

            {/* Error */}
            {error && (
              <div
                className="border border-accent/30 bg-accent-light px-4 py-3 text-sm text-accent font-mono"
                style={{ borderRadius: '2px' }}
              >
                {error}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-border px-6 py-4 flex justify-end gap-3 flex-shrink-0 bg-bg">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-mono text-muted border border-border hover:border-nav hover:text-nav transition-colors"
              style={{ borderRadius: '2px' }}
            >
              Annulla
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 text-sm font-mono text-white bg-nav hover:bg-accent disabled:opacity-50 transition-colors"
              style={{ borderRadius: '2px' }}
            >
              {saving ? 'Salvataggio...' : procedure ? 'Aggiorna' : 'Crea procedura'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
