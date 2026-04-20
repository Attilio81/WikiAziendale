# Wiki Browser UI — Design Spec

**Date:** 2026-04-20  
**Scope:** Add wiki browsing to existing React frontend (no new dependencies)

---

## Goal

Give users a way to read wiki pages compiled by the AI agent, directly in the app — without leaving the procedures management UI.

---

## Architecture

### Routing
No react-router. Simple `useState<'procedures' | 'wiki'>` in `App.tsx`. Two tabs in the existing navbar. URL does not change (acceptable for internal tool).

### New files
- `src/api/wiki.ts` — API client (fetch page list, fetch single page by slug)
- `src/pages/Wiki.tsx` — wiki browser page

### Modified files
- `src/App.tsx` — add Wiki tab + conditional render

---

## UI Layout

### Navbar
Add "Wiki" tab next to "Procedure" in the existing `<nav>`. Active tab has `border-b border-accent` underline (same style as current Procedure link).

### Wiki page: two-panel layout

```
┌──────────────────────────────────────────────────────┐
│  NAVBAR                                              │
├──────────────────┬───────────────────────────────────┤
│  SIDEBAR 260px   │  CONTENT AREA                     │
│                  │                                   │
│  [search input]  │  # Titolo pagina                  │
│                  │                                   │
│  • Ricezione     │  ## Panoramica                    │
│    merci         │  ...                              │
│  • Gestione NC   │                                   │
│  • Spedizioni    │  ## Procedura                     │
│    clienti       │  1. ...                           │
│  ...             │                                   │
│                  │  ## Vedi anche                    │
│                  │  → Reso fornitore                 │
└──────────────────┴───────────────────────────────────┘
```

### Sidebar
- Search input (filters page list client-side by title)
- List of wiki pages: each item shows `titolo` (large) and `slug` (small mono). Clicking selects the page.
- Selected item: navy background, white text
- No pagination needed (wiki expected < 50 pages)

### Content area
- Renders `contenuto_md` via `react-markdown` (already installed)
- Custom prose styles via Tailwind classes (no @tailwindcss/typography needed)
- H1 → `font-display text-3xl font-light text-nav`
- H2 → `font-display text-xl font-light text-nav border-b border-border`
- Links in "Vedi anche" section: if slug matches a known page, render as clickable button that navigates within wiki
- Empty state (no page selected): show `tree_md` from `/wiki/index` rendered as markdown, or a prompt to select a page
- Loading spinner: same `animate-pulse` mono text used in Procedures

### Error / empty states
- No wiki pages yet: "La wiki è vuota. Carica delle procedure e avvia la compilazione."
- Page fetch error: same red border style as Procedures error
- Index missing: graceful — show blank welcome with instructions

---

## API client (`src/api/wiki.ts`)

```typescript
interface WikiPageListItem {
  slug: string
  titolo: string
  links: string[]
  updated_at: string
}

interface WikiPageRead extends WikiPageListItem {
  contenuto_md: string
}

interface WikiIndexRead {
  id: number
  tree_md: string | null
  last_rebuilt_at: string | null
}

fetchWikiPages(): Promise<WikiPageListItem[]>
fetchWikiPage(slug: string): Promise<WikiPageRead>
fetchWikiIndex(): Promise<WikiIndexRead>
```

---

## Constraints
- No new npm packages
- Follow existing code conventions: React Query for data, `handleResponse` pattern, same auth headers
- No URL-based routing
- Italian UI strings (consistent with existing app)
- Mobile not a priority (internal tool)
