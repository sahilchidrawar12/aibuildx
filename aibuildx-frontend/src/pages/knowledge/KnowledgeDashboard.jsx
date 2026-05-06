import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Database, Upload, Search, FileText, BookOpen, Zap } from 'lucide-react'
import { useKnowledgeStore } from '../../stores/knowledgeStore'

function KnowledgeDashboard() {
  const navigate = useNavigate()
  const { stats, documents, fetchStats, fetchDocuments, searchDocuments, isLoading, error } = useKnowledgeStore()
  const [query, setQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [statusMessage, setStatusMessage] = useState('')

  useEffect(() => {
    fetchStats()
    fetchDocuments()
  }, [fetchStats, fetchDocuments])

  const handleSearch = async () => {
    if (!query.trim()) {
      setStatusMessage('Please enter a query to search the knowledge base.')
      setSearchResults([])
      return
    }

    setStatusMessage('Searching knowledge base...')
    const results = await searchDocuments(query)
    setSearchResults(results)
    setStatusMessage(results.length ? `${results.length} results found.` : 'No matching results found.')
  }

  const statsArray = [
    { label: 'Total Documents', value: (stats.totalDocuments ?? 0).toLocaleString(), icon: FileText, color: 'text-blue-400' },
    { label: 'Vector Embeddings', value: `${((stats.vectorEmbeddings ?? 0) / 1000).toFixed(0)}K`, icon: Database, color: 'text-purple-400' },
    { label: 'Search Queries', value: (stats.searchQueries ?? 0).toLocaleString(), icon: Search, color: 'text-green-400' },
    { label: 'Avg Relevance', value: `${stats.avgRelevance ?? 0}%`, icon: Zap, color: 'text-yellow-400' }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Knowledge Base</h1>
          <p className="text-secondary-400 mt-1">Manage documents and vector embeddings for AI-powered search.</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="btn-primary"
        >
          <Upload className="w-5 h-5 mr-2" />
          Upload Documents
        </motion.button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsArray.map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-secondary-400 text-sm font-medium">{stat.label}</p>
                <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
              </div>
              <div className="p-3 bg-secondary-700 rounded-lg">
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Documents */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <BookOpen className="w-5 h-5 mr-2 text-primary-400" />
            Recent Documents
          </h2>

          <div className="space-y-3">
            {documents.slice(0, 4).map((doc, index) => (
              <div key={doc.id || index} className="flex items-center justify-between p-3 bg-secondary-700/50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`p-2 rounded ${
                    doc.status === 'indexed' ? 'bg-green-600/20' :
                    doc.status === 'processing' ? 'bg-yellow-600/20' :
                    'bg-blue-600/20'
                  }`}>
                    <FileText className={`w-4 h-4 ${
                      doc.status === 'indexed' ? 'text-green-400' :
                      doc.status === 'processing' ? 'text-yellow-400' :
                      'text-blue-400'
                    }`} />
                  </div>
                  <div>
                    <p className="text-white font-medium text-sm">{doc.name}</p>
                    <p className="text-secondary-400 text-xs">{doc.type} • {doc.size}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    doc.status === 'indexed' ? 'bg-green-500/20 text-green-400' :
                    doc.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {doc.status}
                  </span>
                  <span className="text-secondary-400 text-xs">{doc.uploaded}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Search & Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-secondary-800 border border-secondary-700 rounded-lg p-6"
        >
          <h2 className="text-xl font-bold text-white mb-4 flex items-center">
            <Search className="w-5 h-5 mr-2 text-primary-400" />
            Knowledge Actions
          </h2>

          <div className="space-y-4">
            <div className="relative">
              <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search knowledge base..."
                className="input pl-10 w-full"
              />
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleSearch}
                className="flex items-center justify-center gap-2 rounded-3xl bg-primary-600/20 border border-primary-500/30 px-4 py-3 text-left hover:bg-primary-600/30 transition-colors"
              >
                <Database className="w-5 h-5 text-primary-400" />
                <span className="text-white font-medium">Run Search</span>
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => navigate('/superadmin/knowledge/upload')}
                className="flex items-center justify-center gap-2 rounded-3xl bg-secondary-700/50 border border-secondary-600 px-4 py-3 hover:bg-secondary-700 transition-colors"
              >
                <Upload className="w-5 h-5 text-secondary-400" />
                <span className="text-white font-medium">Upload Documents</span>
              </motion.button>
            </div>

            <div className="rounded-3xl border border-secondary-700 bg-secondary-900 p-4 text-sm text-secondary-300">
              {error ? `Error: ${error}` : statusMessage || 'Search documents, upload new sources, or re-index the knowledge base.'}
            </div>
          </div>
        </motion.div>
      </div>

      {searchResults.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="space-y-3"
        >
          <h2 className="text-lg font-semibold text-white">Search Results</h2>
          {searchResults.map((doc, index) => (
            <div key={`${doc.id || doc.query}-${index}`} className="rounded-3xl border border-secondary-700 bg-secondary-900 p-4">
              <p className="text-white font-medium">{doc.name || doc.query}</p>
              <p className="text-secondary-400 text-sm mt-1">{doc.snippet || doc.type}</p>
              <p className="text-secondary-500 text-xs mt-2">Relevance: {Math.round((doc.score ?? 0) * 100)}%</p>
            </div>
          ))}
        </motion.div>
      )}
    </div>
  )
}

export default KnowledgeDashboard