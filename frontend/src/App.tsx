import { Procedures } from './pages/Procedures'

export default function App() {
  return (
    <div className="min-h-screen bg-bg">
      {/* Navigation */}
      <nav className="bg-nav text-white border-b-2 border-accent">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-baseline gap-8">
          <span className="font-display text-xl font-light tracking-wide text-white/90">
            Wiki<span className="text-accent font-semibold">Aziendale</span>
          </span>
          <div className="flex gap-6 text-sm">
            <a href="/" className="text-white/70 hover:text-white border-b border-accent pb-0.5 transition-colors">
              Procedure
            </a>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-10">
        <Procedures />
      </main>
    </div>
  )
}
