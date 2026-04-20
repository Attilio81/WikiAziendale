import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  fetchProcedures,
  createProcedure,
  updateProcedure,
  deleteProcedure,
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
        <button
          onClick={() => open()}
          className="px-5 py-2.5 bg-nav text-white text-sm font-mono hover:bg-accent transition-colors flex items-center gap-2"
          style={{ borderRadius: '2px' }}
        >
          <span className="text-accent group-hover:text-white text-lg leading-none">+</span>
          Nuova procedura
        </button>
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
