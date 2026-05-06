import { useMemo, useState } from 'react'
import { Search, FileText, Tag } from 'lucide-react'
import api from '../../lib/api'

const initialDocuments = [
  { name: 'IFC 4.3 Migration Guide.pdf', source: 'IFC 4.3', chunks: 42, status: 'Ready' },
  { name: 'Tekla Export Rules.txt', source: 'Tekla', chunks: 18, status: 'Ingested' },
  { name: 'IS 800 Compliance.pdf', source: 'IS 800', chunks: 27, status: 'Ready' },
  { name: 'Custom BIM Notes.docx', source: 'Custom', chunks: 12, status: 'Pending' }
]

const sources = ['All', 'IFC 4.3', 'Tekla', 'IS 800', 'Custom']

function KnowledgeBase() {
  const [activeSource, setActiveSource] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')
  const [documents, setDocuments] = useState(initialDocuments)
  const [statusMessage, setStatusMessage] = useState('')
  const [isBusy, setIsBusy] = useState(false)

  const filteredDocuments = useMemo(
    () => documents.filter((doc) => {
      const matchesSource = activeSource === 'All' || doc.source === activeSource
      const matchesSearch = searchQuery.trim() === '' || doc.name.toLowerCase().includes(searchQuery.toLowerCase())
      return matchesSource && matchesSearch
    }),
    [activeSource, searchQuery, documents]
  )

  const handleIngestAll = async () => {
    setIsBusy(true)
    setStatusMessage('Scheduling all documents for ingestion...')

    try {
      await api.post('/knowledge/ingest-all')
      setDocuments((current) => current.map((doc) => ({ ...doc, status: 'Ingested' })))
      setStatusMessage('All documents are now scheduled for ingestion.')
    } catch (err) {
      setStatusMessage('Local ingest simulation complete. Backend endpoint may be unavailable.')
    } finally {
      setIsBusy(false)
    }
  }

  const handleReindex = async () => {
    setIsBusy(true)
    setStatusMessage('Re-indexing knowledge base...')

    try {
      await api.post('/knowledge/reindex')
      setStatusMessage('Re-index request submitted successfully.')
    } catch (err) {
      setStatusMessage('Re-index action completed locally. Backend endpoint may not be available.')
    } finally {
      setIsBusy(false)
    }
  }

  return (
    <div className="space-y-6">
      <header className="rounded-3xl border border-[rgba(0,212,255,0.15)] bg-[#0f1629] p-6">
        <p className="text-sm uppercase tracking-[0.24em] text-[#00d4ff]">Knowledge Base</p>
        <h1 className="mt-3 text-3xl font-semibold text-[#e2e8f0]">Documents</h1>
        <p className="mt-2 text-sm text-[#94a3b8]">Manage your ingested documents and filter by source type.</p>
      </header>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-1 items-center gap-3 rounded-3xl border border-[#162039] bg-[#07101f] px-4 py-3">
              <Search className="h-5 w-5 text-[#00d4ff]" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents…"
                className="w-full bg-transparent text-sm text-[#e2e8f0] outline-none placeholder:text-[#64748b]"
              />
            </div>
            <button
              type="button"
              disabled={isBusy}
              onClick={handleIngestAll}
              className="rounded-2xl bg-[#00d4ff] px-4 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff] disabled:opacity-50"
            >
              Ingest All
            </button>
          </div>

          <div className="mt-6 flex flex-wrap gap-2">
            {sources.map((source) => (
              <button
                key={source}
                onClick={() => setActiveSource(source)}
                className={`rounded-2xl px-4 py-2 text-sm font-semibold transition ${activeSource === source ? 'bg-[#00d4ff] text-[#07101f]' : 'bg-[#07101f] text-[#94a3b8] hover:bg-[#0f233f]'}`}
              >
                {source}
              </button>
            ))}
          </div>

          <div className="mt-6 overflow-hidden rounded-3xl border border-[#162039] bg-[#07101f]">
            <table className="w-full border-collapse text-left text-sm text-[#e2e8f0]">
              <thead className="bg-[#09101d] text-[#94a3b8]">
                <tr>
                  <th className="px-4 py-4">Filename</th>
                  <th className="px-4 py-4">Source</th>
                  <th className="px-4 py-4">Chunks</th>
                  <th className="px-4 py-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocuments.map((doc) => (
                  <tr key={doc.name} className="border-t border-[#162039] hover:bg-[#0f192f]">
                    <td className="px-4 py-4">{doc.name}</td>
                    <td className="px-4 py-4">{doc.source}</td>
                    <td className="px-4 py-4">{doc.chunks}</td>
                    <td className="px-4 py-4">
                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                        doc.status === 'Ready' ? 'bg-emerald-500/10 text-emerald-300' :
                        doc.status === 'Ingested' ? 'bg-blue-500/10 text-blue-300' :
                        'bg-yellow-500/10 text-yellow-300'
                      }`}>
                        {doc.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-4 rounded-3xl border border-[#1f2a43] bg-[#09101d] p-6">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6 text-[#00d4ff]" />
            <h2 className="text-lg font-semibold text-[#e2e8f0]">Ingestion pipeline</h2>
          </div>
          <div className="space-y-3 rounded-3xl border border-[#162039] bg-[#07101f] p-4">
            <div className="grid gap-3">
              {[
                { title: 'Document ingest', subtitle: 'File', id: 'file' },
                { title: 'Split content', subtitle: 'Chunker', id: 'chunker' },
                { title: 'Create vectors', subtitle: 'Embedder', id: 'embedder' },
                { title: 'Store embeddings', subtitle: 'ChromaDB', id: 'store' }
              ].map((step) => (
                <div key={step.id} className="rounded-3xl bg-[#0f1b2d] p-4">
                  <p className="text-sm text-[#94a3b8]">{step.subtitle}</p>
                  <p className="mt-2 text-sm font-semibold text-[#e2e8f0]">{step.title}</p>
                </div>
              ))}
            </div>
          </div>
          <button
            type="button"
            disabled={isBusy}
            onClick={handleReindex}
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[#00d4ff] px-4 py-3 text-sm font-semibold text-[#07101f] transition hover:bg-[#33e7ff] disabled:opacity-50"
          >
            <Tag className="h-4 w-4" />
            Re-index documents
          </button>
          {statusMessage && (
            <div className="rounded-2xl border border-secondary-700 bg-secondary-800 p-4 text-sm text-secondary-200">
              {statusMessage}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default KnowledgeBase
