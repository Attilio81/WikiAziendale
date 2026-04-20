import { create } from 'zustand'
import type { Procedure } from '../api/procedures'

interface ModalState {
  isOpen: boolean
  editingProcedure: Procedure | null
  open: (procedure?: Procedure) => void
  close: () => void
}

export const useModalStore = create<ModalState>((set) => ({
  isOpen: false,
  editingProcedure: null,
  open: (procedure) => set({ isOpen: true, editingProcedure: procedure ?? null }),
  close: () => set({ isOpen: false, editingProcedure: null }),
}))
