import { create } from 'zustand'

export const useChatStore = create(set => ({
  open: false,
  toggle: () => set(s => ({ open: !s.open })),
  setOpen: (v) => set({ open: v }),
}))
