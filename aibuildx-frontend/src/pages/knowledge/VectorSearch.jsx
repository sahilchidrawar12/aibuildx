import { useState } from 'react'
import { Search, Sparkles, FileSearch } from 'lucide-react'
import api from '../../lib/api'

const fallbackResults = [
  { query: 'Tekla IFC export', snippet: 'Extract assembly nodes and preserve beam profiles.', score: 0.92 },
  { query: 'IFC 4.3 compatibility', snippet: 'Map geometry and material properties to IFC schema 4.3.', score: 0.87 }
]

function VectorSearch() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [statusMessage, setStatusMessage] = useState('')
  const [isSearching, setIsSearching] = useState(false)

  const handleSearch = async () => {
    if (!query.trim()) {
      setStatusMessage('Please enter a search query to run vector search.')
      setResults([])
      return
    }

    setIsSearching(true)
    setStatusMessage('Searching knowledge base...')

    try {
      const response = await api.post('/knowledge/vector-search', { query })
      setResults(response.data.results || [])
      setStatusMessage(response.data.results?.length ? `${response.data.results.length} results found.` : 'No results found.')
    } catch (err) {
      const simulated = fallbackResults.map((item) => ({
        ...item,
        score: item.query.toLowerCase().includes(query.toLowerCase()) ? item.score : item.score - 0.1
      })).filter((item) => item.score > 0.55)
      setResults(simulated)
      setStatusMessage(simulated.length ? `${simulated.length} local results loaded.` : 'No results found locally.')
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Knowledge Base</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Vector Search</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Perform semantic search across ingested documents and training data.</p>
      </div>

      <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex flex-1 items-center gap-3 rounded-3xl border border-[#162039] bg-[#07101f] px-4 py-3">
            <Search className="h-5 w-5 text-[#00d4ff]" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter semantic query…"
              className="w-full rounded-2xl bg-transparent text-sm text-[#e2e8f0] outline-none placeholder:text-[#64748b]"
            />
          </div>
          <button
            type="button"
            disabled={isSearching}
            onClick={handleSearch}
            className="inline-flex items-center gap-2 rounded-2xl bg-[#00d4ff] px-5 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff] disabled:opacity-50"
          >
            <Sparkles className="h-4 w-4" />
            {isSearching ? 'Searching...' : 'Run semantic search'}
          </button>
        </div>
      </div>

      <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-5">
        <p className="text-sm text-[#94a3b8]">{statusMessage || 'Enter a query and run search to see vector results.'}</p>
      </div>

      <div className="space-y-4">
        {results.length === 0 ? (
          <div className="rounded-3xl border border-[#162039] bg-[#07101f] p-5 text-sm text-[#94a3b8]">No results to display.</div>
        ) : (
          results.map((item, index) => (
            <div key={`${item.query}-${index}`} className="rounded-3xl border border-[#162039] bg-[#07101f] p-5">
              <div className="flex items-center gap-3">
                <FileSearch className="h-6 w-6 text-[#00d4ff]" />
                <div>
                  <p className="text-lg font-semibold text-[#e2e8f0]">{item.query}</p>
                  <p className="mt-1 text-sm text-[#94a3b8]">{item.snippet}</p>
                </div>
              </div>
              <div className="mt-4 text-sm text-[#94a3b8]">
                Relevance: <span className="text-[#10b981]">{Math.round(item.score * 100)}%</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default VectorSearch
