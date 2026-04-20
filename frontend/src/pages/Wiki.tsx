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

  const { data: index, isError: indexError } = useQuery({
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
        {pageLoading && (
          <p className="text-xs font-mono tracking-widest text-muted uppercase animate-pulse">
            Caricamento pagina...
          </p>
        )}

        {!selectedSlug && indexError && (
          <p className="text-xs font-mono text-accent py-4">
            Errore di caricamento dell'indice wiki.
          </p>
        )}

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
