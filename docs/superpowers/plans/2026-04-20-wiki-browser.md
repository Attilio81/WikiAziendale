# Wiki Browser UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a two-panel wiki browser (sidebar page list + markdown viewer) to the existing React frontend, accessible via a new "Wiki" tab in the navbar.

**Architecture:** State-based routing (`useState<'procedures'|'wiki'>` in `App.tsx`) — no react-router needed. Sidebar lists wiki pages from `GET /api/v1/wiki/pages`; content area fetches and renders the selected page markdown via `GET /api/v1/wiki/pages/{slug}`. `react-markdown` (already installed, v9) renders the markdown with custom Tailwind-styled components.

**Tech Stack:** React 18, TypeScript, React Query v5, Tailwind CSS, react-markdown v9

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `frontend/src/api/wiki.ts` | Create | API client: fetch page list, single page, wiki index |
| `frontend/src/pages/Wiki.tsx` | Create | Two-panel wiki browser: sidebar + markdown viewer |
| `frontend/src/App.tsx` | Modify | Add Wiki tab + state-based routing |

---

### Task 1: API client for wiki endpoints

**Files:**
- Create: `frontend/src/api/wiki.ts`

**Context:** The backend exposes three wiki endpoints (all require `X-API-Key` header, same as procedures):
- `GET /api/v1/wiki/pages` → `WikiPageListItem[]`
- `GET /api/v1/wiki/pages/{slug}` → `WikiPageRead`
- `GET /api/v1/wiki/index` → `WikiIndexRead`

Exact backend schemas (from `backend/app/schemas/wiki.py`):
- `WikiPageListItem`: `{ id: string, slug: string, titolo: string, last_compiled_at: string|null, compilation_model: string|null, version: number, source_raw_ids: any[]|null }`
- `WikiPageRead`: adds `contenuto_md: string, links: any[]|null`
- `WikiIndexRead`: `{ id: number, tree_md: string|null, last_rebuilt_at: string|null }`

No tests exist for frontend code in this project. Verify manually by running the dev server.

- [ ] **Step 1: Create `frontend/src/api/wiki.ts`**

```typescript
const BASE = `${import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'}`
const API_KEY = import.meta.env.VITE_API_KEY ?? 'dev-change-me'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY,
}

export interface WikiPageListItem {
  id: string
  slug: string
  titolo: string
  last_compiled_at: string | null
  compilation_model: string | null
  version: number
  source_raw_ids: string[] | null
}

export interface WikiPageRead extends WikiPageListItem {
  contenuto_md: string
  links: string[] | null
}

export interface WikiIndexRead {
  id: number
  tree_md: string | null
  last_rebuilt_at: string | null
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  if (res.status === 204) return undefined as T
  return res.json()
}

export async function fetchWikiPages(): Promise<WikiPageListItem[]> {
  const res = await fetch(`${BASE}/wiki/pages`, { headers })
  return handleResponse(res)
}

export async function fetchWikiPage(slug: string): Promise<WikiPageRead> {
  const res = await fetch(`${BASE}/wiki/pages/${encodeURIComponent(slug)}`, { headers })
  return handleResponse(res)
}

export async function fetchWikiIndex(): Promise<WikiIndexRead> {
  const res = await fetch(`${BASE}/wiki/index`, { headers })
  return handleResponse(res)
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/api/wiki.ts
git commit -m "feat(frontend): add wiki API client"
```

---

### Task 2: Wiki browser page component

**Files:**
- Create: `frontend/src/pages/Wiki.tsx`

**Context:** Two-panel layout:
- Left sidebar (fixed 256px): search input + scrollable list of wiki pages. Clicking selects a page.
- Right content area: renders selected page `contenuto_md` with react-markdown. When nothing selected, shows `tree_md` from the wiki index (or an empty-state message).

Existing design tokens (from `tailwind.config.js`):
- Colors: `bg` #F7F3EE, `surface` #FFFFFF, `nav` #1B2840, `accent` #B5492C, `accent-light` #F0E0DA, `border` #E2DDD8, `muted` #6B6B6B
- Fonts: `font-display` (Fraunces serif), `font-sans` (DM Sans), `font-mono` (DM Mono)
- Border radius: all `2px`

react-markdown v9 component map: pass a `components` prop typed as `import type { Components } from 'react-markdown'`.

Internal wiki links: the compiler writes links using the slug as the href (e.g., `[Ricezione merci](ricezione-merci)`). When the `href` matches a known page slug, render a clickable button that sets `selectedSlug` instead of opening a new tab.

- [ ] **Step 1: Create `frontend/src/pages/Wiki.tsx`**

```tsx
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import type { Components } from 'react-markdown'
import {
  fetchWikiPages,
  fetchWikiPage,
  fetchWikiIndex,
  type WikiPageListItem,
} from '../api/wiki'

export function Wiki() {
  const [selectedSlug, setSelectedSlug] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const { data: pages = [], isLoading: pagesLoading, isError: pagesError } = useQuery({
    queryKey: ['wiki-pages'],
    queryFn: fetchWikiPages,
  })

  const { data: page, isLoading: pageLoading } = useQuery({
    queryKey: ['wiki-page', selectedSlug],
    queryFn: () => fetchWikiPage(selectedSlug!),
    enabled: selectedSlug !== null,
  })

  const { data: index } = useQuery({
    queryKey: ['wiki-index'],
    queryFn: fetchWikiIndex,
    enabled: selectedSlug === null,
  })

  const filteredPages: WikiPageListItem[] = pages.filter(p =>
    p.titolo.toLowerCase().includes(search.toLowerCase()) ||
    p.slug.toLowerCase().includes(search.toLowerCase())
  )

  const makeComponents = (knownSlugs: string[]): Components => ({
    h1({ children }) {
      return (
        <h1 className="font-display text-3xl font-light text-nav tracking-wide mb-6 pb-4 border-b-2 border-nav">
          {children}
        </h1>
      )
    },
    h2({ children }) {
      return (
        <h2 className="font-display text-xl font-light text-nav mt-8 mb-3 pb-2 border-b border-border">
          {children}
        </h2>
      )
    },
    h3({ children }) {
      return <h3 className="font-sans font-semibold text-nav mt-5 mb-2 text-sm">{children}</h3>
    },
    p({ children }) {
      return <p className="text-sm leading-relaxed text-gray-800 mb-3">{children}</p>
    },
    ul({ children }) {
      return <ul className="list-disc list-outside ml-5 text-sm text-gray-800 mb-3 space-y-1">{children}</ul>
    },
    ol({ children }) {
      return <ol className="list-decimal list-outside ml-5 text-sm text-gray-800 mb-3 space-y-1">{children}</ol>
    },
    li({ children }) {
      return <li className="leading-relaxed">{children}</li>
    },
    code({ children }) {
      return (
        <code className="font-mono text-xs bg-surface border border-border px-1 py-0.5 text-accent">
          {children}
        </code>
      )
    },
    a({ href, children }) {
      const slug = href ?? ''
      if (knownSlugs.includes(slug)) {
        return (
          <button
            onClick={() => setSelectedSlug(slug)}
            className="text-accent hover:underline font-mono text-xs"
          >
            {children}
          </button>
        )
      }
      return (
        <a href={href} className="text-accent hover:underline" target="_blank" rel="noreferrer">
          {children}
        </a>
      )
    },
  })

  const knownSlugs = pages.map(p => p.slug)
  const components = makeComponents(knownSlugs)

  return (
    <div className="flex animate-fade-in" style={{ minHeight: 'calc(100vh - 73px)' }}>
      {/* Sidebar */}
      <aside className="w-64 shrink-0 border-r border-border bg-surface flex flex-col">
        <div className="p-4 border-b border-border">
          <input
            type="text"
            placeholder="Cerca pagina..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full border border-border px-3 py-2 text-sm bg-bg focus:outline-none focus:border-nav transition-colors"
            style={{ borderRadius: '2px' }}
          />
        </div>

        <nav className="flex-1 overflow-y-auto">
          {pagesLoading && (
            <p className="text-xs font-mono tracking-widest text-muted uppercase animate-pulse px-4 py-4">
              Caricamento...
            </p>
          )}
          {pagesError && (
            <p className="text-xs font-mono text-accent px-4 py-4">
              Errore di connessione al backend.
            </p>
          )}
          {!pagesLoading && !pagesError && pages.length === 0 && (
            <p className="text-xs font-mono text-muted px-4 py-4">
              Nessuna pagina wiki ancora.
            </p>
          )}
          {filteredPages.map(p => (
            <button
              key={p.slug}
              onClick={() => setSelectedSlug(p.slug)}
              className={`w-full text-left px-4 py-3 border-b border-border transition-colors ${
                selectedSlug === p.slug
                  ? 'bg-nav text-white'
                  : 'hover:bg-accent-light'
              }`}
            >
              <div
                className={`text-sm font-sans truncate ${
                  selectedSlug === p.slug ? 'text-white' : 'text-nav'
                }`}
              >
                {p.titolo}
              </div>
              <div
                className={`text-xs font-mono mt-0.5 truncate ${
                  selectedSlug === p.slug ? 'text-white/60' : 'text-muted'
                }`}
              >
                {p.slug}
              </div>
            </button>
          ))}
        </nav>

        <div className="p-3 border-t border-border">
          <p className="text-xs font-mono text-muted">
            {pages.length} {pages.length === 1 ? 'pagina' : 'pagine'}
          </p>
        </div>
      </aside>

      {/* Content area */}
      <main className="flex-1 overflow-y-auto px-10 py-8">
        {/* Loading selected page */}
        {pageLoading && (
          <p className="text-xs font-mono tracking-widest text-muted uppercase animate-pulse">
            Caricamento pagina...
          </p>
        )}

        {/* No page selected — show index or empty state */}
        {!selectedSlug && !pageLoading && (
          <>
            {index?.tree_md ? (
              <article className="max-w-3xl">
                <ReactMarkdown components={components}>{index.tree_md}</ReactMarkdown>
              </article>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-24 text-center">
                <h2 className="font-display text-3xl font-light text-nav mb-3">
                  Wiki<span className="text-accent">Aziendale</span>
                </h2>
                <p className="text-sm text-muted font-mono max-w-sm">
                  La wiki è vuota. Carica delle procedure e avvia la compilazione per generare le pagine.
                </p>
              </div>
            )}
          </>
        )}

        {/* Selected page content */}
        {page && !pageLoading && (
          <article className="max-w-3xl">
            <ReactMarkdown components={components}>{page.contenuto_md}</ReactMarkdown>
            {page.last_compiled_at && (
              <p className="mt-10 text-xs font-mono text-muted border-t border-border pt-4">
                Compilato il {new Date(page.last_compiled_at).toLocaleString('it-IT')} — v{page.version}
                {page.compilation_model && ` — ${page.compilation_model}`}
              </p>
            )}
          </article>
        )}
      </main>
    </div>
  )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/pages/Wiki.tsx
git commit -m "feat(frontend): add Wiki browser page component"
```

---

### Task 3: Wire Wiki tab into App.tsx

**Files:**
- Modify: `frontend/src/App.tsx` (currently 26 lines)

**Context:** Current `App.tsx` has a single hardcoded `<a href="/">Procedure</a>` link and always renders `<Procedures />`. Replace with stateful tab navigation.

The Wiki page uses a full-height two-panel layout and must NOT be wrapped in the `max-w-7xl mx-auto px-6 py-10` container used by Procedures. Render each page conditionally.

Navbar height is `py-4` top + bottom + font size + border ≈ 73px. The `Wiki` component uses `minHeight: calc(100vh - 73px)` to fill the viewport.

- [ ] **Step 1: Replace `frontend/src/App.tsx` entirely**

```tsx
import { useState } from 'react'
import { Procedures } from './pages/Procedures'
import { Wiki } from './pages/Wiki'

type Page = 'procedures' | 'wiki'

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('procedures')

  const navLink = (page: Page, label: string) => (
    <button
      onClick={() => setCurrentPage(page)}
      className={`text-sm transition-colors pb-0.5 ${
        currentPage === page
          ? 'text-white border-b border-accent'
          : 'text-white/50 hover:text-white/80'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="min-h-screen bg-bg">
      <nav className="bg-nav text-white border-b-2 border-accent">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-baseline gap-8">
          <span className="font-display text-xl font-light tracking-wide text-white/90">
            Wiki<span className="text-accent font-semibold">Aziendale</span>
          </span>
          <div className="flex gap-6">
            {navLink('procedures', 'Procedure')}
            {navLink('wiki', 'Wiki')}
          </div>
        </div>
      </nav>

      {currentPage === 'procedures' && (
        <main className="max-w-7xl mx-auto px-6 py-10">
          <Procedures />
        </main>
      )}
      {currentPage === 'wiki' && <Wiki />}
    </div>
  )
}
```

- [ ] **Step 2: Verify TypeScript compiles**

Run from `frontend/`:
```bash
npx tsc --noEmit
```
Expected: no errors.

- [ ] **Step 3: Start dev server and verify manually**

```bash
npm run dev -- --port 5175
```

Open `http://localhost:5175`:
1. Navbar shows "Procedure" and "Wiki" tabs — active tab has underline
2. Click "Wiki" → sidebar appears on left, content area on right
3. If wiki is empty: content area shows empty-state message
4. If wiki has pages: sidebar lists them; clicking one renders markdown in content area
5. Click "Procedure" → returns to procedure table

- [ ] **Step 4: Commit**

```bash
git add frontend/src/App.tsx
git commit -m "feat(frontend): add Wiki tab with state-based routing"
```

---

## Self-Review

**Spec coverage check:**
- ✅ Wiki tab in navbar → Task 3
- ✅ Sidebar with page list → Task 2
- ✅ Search filtering client-side → Task 2
- ✅ Markdown viewer with custom Tailwind styles → Task 2
- ✅ Internal wiki links navigable → Task 2 (`makeComponents` + slug check)
- ✅ Empty state (no wiki pages) → Task 2
- ✅ Index shown when no page selected → Task 2
- ✅ No new npm packages → confirmed (react-markdown already in deps)
- ✅ Italian UI strings → confirmed throughout
- ✅ Follows existing code conventions (handleResponse, React Query, Tailwind tokens) → Task 1 + 2

**Placeholder scan:** None found.

**Type consistency:**
- `WikiPageListItem` defined in Task 1, used in Task 2 ✅
- `fetchWikiPages`, `fetchWikiPage`, `fetchWikiIndex` defined in Task 1, imported in Task 2 ✅
- `Wiki` component defined in Task 2, imported in Task 3 ✅
