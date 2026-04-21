import { useState, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchProcedures,
  createProcedure,
  updateProcedure,
  deleteProcedure,
  uploadProcedure,
  type Procedure,
  type ProcedureCreate,
} from '../api/procedures'
import { ProcedureTable } from '../components/ProcedureTable'
import { ProcedureModal } from '../components/ProcedureModal'
import { useModalStore } from '../store/modal'

export function Procedures() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [categoria, setCategoria] = useState('')
  const [uploadError, setUploadError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const qc = useQueryClient()
  const { isOpen, editingProcedure, open, close } = useModalStore()

  const { data, isLoading, isError } = useQuery({
    queryKey: ['procedures', page, search, categoria],
    queryFn: () =>
      fetchProcedures({
        page,
        q: search || undefined,
        categoria: categoria || undefined,
      }),
  })

  const createMutation = useMutation({
    mutationFn: createProcedure,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['procedures'] }),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ProcedureCreate> }) =>
      updateProcedure(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['procedures'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProcedure,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['procedures'] }),
  })

  const uploadMutation = useMutation({
    mutationFn: (file: File) => uploadProcedure(file),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['procedures'] })
      setUploadError(null)
    },
    onError: (err: Error) => setUploadError(err.message),
  })

  async function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadError(null)
    await uploadMutation.mutateAsync(file)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  async function handleSave(formData: ProcedureCreate) {
    if (editingProcedure) {
      await updateMutation.mutateAsync({ id: editingProcedure.id, data: formData })
    } else {
      await createMutation.mutateAsync(formData)
    }
  }

  function handleDelete(proc: Procedure) {
    if (window.confirm(`Eliminare la procedura "${proc.titolo}"?`)) {
      deleteMutation.mutate(proc.id)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex items-baseline justify-between border-b-2 border-nav pb-4">
        <div>
          <h1 className="font-display text-3xl font-light text-nav tracking-wide">Procedure</h1>
          {data && (
            <p className="mt-1 text-xs font-mono text-muted tracking-widest uppercase">
              {data.total} procedure nel sistema
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={handleFileChange}
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadMutation.isPending}
            className="px-5 py-2.5 border border-nav text-nav text-sm font-mono hover:bg-nav hover:text-white transition-colors flex items-center gap-2 disabled:opacity-50"
            style={{ borderRadius: '2px' }}
          >
            {uploadMutation.isPending ? '...' : '↑ Carica file'}
          </button>
          <button
            onClick={() => open()}
            className="px-5 py-2.5 bg-nav text-white text-sm font-mono hover:bg-accent transition-colors flex items-center gap-2"
            style={{ borderRadius: '2px' }}
          >
            <span className="text-accent group-hover:text-white text-lg leading-none">+</span>
            Nuova procedura
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Cerca nel titolo..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(1)
            }}
            className="w-full border border-border px-3 py-2 text-sm bg-surface focus:outline-none focus:border-nav transition-colors"
            style={{ borderRadius: '2px' }}
          />
        </div>
        <input
          type="text"
          placeholder="Categoria..."
          value={categoria}
          onChange={(e) => {
            setCategoria(e.target.value)
            setPage(1)
          }}
          className="w-44 border border-border px-3 py-2 text-sm bg-surface focus:outline-none focus:border-nav transition-colors"
          style={{ borderRadius: '2px' }}
        />
      </div>

      {/* Upload error */}
      {uploadError && (
        <div
          className="border border-accent/30 bg-accent-light px-5 py-3 text-sm font-mono text-accent flex justify-between items-center"
          style={{ borderRadius: '2px' }}
        >
          <span>Errore upload: {uploadError}</span>
          <button onClick={() => setUploadError(null)} className="ml-4 opacity-60 hover:opacity-100">✕</button>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="text-center py-16">
          <p className="text-xs font-mono tracking-widest text-muted uppercase animate-pulse">
            Caricamento...
          </p>
        </div>
      )}

      {/* Error */}
      {isError && (
        <div
          className="border border-accent/30 bg-accent-light px-5 py-4 text-sm font-mono text-accent"
          style={{ borderRadius: '2px' }}
        >
          Impossibile connettersi al backend. Verificare che il server sia attivo su localhost:8000.
        </div>
      )}

      {/* Table */}
      {data && (
        <ProcedureTable
          data={data}
          onEdit={open}
          onDelete={handleDelete}
          page={page}
          onPageChange={setPage}
        />
      )}

      {/* Modal */}
      {isOpen && (
        <ProcedureModal
          procedure={editingProcedure}
          onSave={handleSave}
          onClose={close}
        />
      )}
    </div>
  )
}
