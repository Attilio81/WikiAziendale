import { useState } from 'react'
import { Procedures } from './pages/Procedures'
import { Wiki } from './pages/Wiki'
import { Chat } from './pages/Chat'

type Page = 'procedures' | 'wiki' | 'chat'

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('procedures')
  const [wikiSlug, setWikiSlug] = useState<string | undefined>(undefined)

  function handleNavigateToWiki(slug: string) {
    setWikiSlug(slug)
    setCurrentPage('wiki')
  }

  function handleNavClick(page: Page) {
    setCurrentPage(page)
    if (page !== 'wiki') setWikiSlug(undefined)
  }

  const navLink = (page: Page, label: string) => (
    <button
      onClick={() => handleNavClick(page)}
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
            {navLink('chat', 'Chat')}
          </div>
        </div>
      </nav>

      {currentPage === 'procedures' && (
        <main className="max-w-7xl mx-auto px-6 py-10">
          <Procedures />
        </main>
      )}
      {currentPage === 'wiki' && <Wiki initialSlug={wikiSlug} />}
      {currentPage === 'chat' && (
        <main className="max-w-7xl mx-auto">
          <Chat onNavigateToWiki={handleNavigateToWiki} />
        </main>
      )}
    </div>
  )
}
