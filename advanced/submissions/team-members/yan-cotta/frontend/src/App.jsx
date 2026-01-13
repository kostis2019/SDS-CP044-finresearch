import { useState, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import {
  Search,
  TrendingUp,
  Brain,
  FileText,
  Settings,
  Loader2,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sparkles,
  Bot,
  ChevronDown,
  ChevronUp,
  Clock,
  Cpu,
  Download,
} from 'lucide-react'

// =============================================================================
// Configuration
// =============================================================================

const API_BASE_URL = '/api'

const MODEL_PROVIDERS = [
  { id: 'openai', name: 'OpenAI', description: 'GPT-4o-mini + GPT-3.5' },
  { id: 'groq', name: 'Groq', description: 'LLaMA 3 (Fast)', disabled: true },
]

// =============================================================================
// Custom Hooks
// =============================================================================

function useResearch() {
  const [isLoading, setIsLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [logs, setLogs] = useState([])
  const [error, setError] = useState(null)
  const [duration, setDuration] = useState(null)

  const runResearch = useCallback(async (ticker, options = {}) => {
    setIsLoading(true)
    setError(null)
    setReport(null)
    setLogs(['Starting research...'])
    setDuration(null)

    try {
      const response = await fetch(`${API_BASE_URL}/research`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ticker: ticker.toUpperCase(),
          company_name: options.companyName || null,
          reset_memory: options.resetMemory || false,
          model_provider: options.modelProvider || 'openai',
          sequential_mode: true, // Always use sequential for stability
        }),
      })

      const data = await response.json()

      if (data.success) {
        setReport(data.report)
        setLogs(data.logs || [])
        setDuration(data.duration_seconds)
      } else {
        setError(data.error || 'Research failed')
        setLogs(data.logs || [])
      }
    } catch (err) {
      setError(err.message || 'Network error')
      setLogs((prev) => [...prev, `Error: ${err.message}`])
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clearResults = useCallback(() => {
    setReport(null)
    setLogs([])
    setError(null)
    setDuration(null)
  }, [])

  return {
    isLoading,
    report,
    logs,
    error,
    duration,
    runResearch,
    clearResults,
  }
}

// =============================================================================
// Components
// =============================================================================

function Header() {
  return (
    <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-white/10 p-2 rounded-lg">
              <TrendingUp className="h-8 w-8" />
            </div>
            <div>
              <h1 className="text-2xl font-bold">FinResearch AI</h1>
              <p className="text-primary-200 text-sm">
                Multi-Agent Financial Research System
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2 text-primary-200">
            <Bot className="h-5 w-5" />
            <span className="text-sm">Powered by CrewAI</span>
          </div>
        </div>
      </div>
    </header>
  )
}

function SearchForm({ onSearch, isLoading }) {
  const [ticker, setTicker] = useState('')
  const [showSettings, setShowSettings] = useState(false)
  const [resetMemory, setResetMemory] = useState(false)
  const [modelProvider, setModelProvider] = useState('openai')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (ticker.trim() && !isLoading) {
      onSearch(ticker.trim(), { resetMemory, modelProvider })
    }
  }

  const quickTickers = ['AAPL', 'TSLA', 'GOOGL', 'MSFT', 'NVDA', 'AMZN']

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <form onSubmit={handleSubmit}>
        {/* Main Search Input */}
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Enter stock ticker (e.g., AAPL)"
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-lg font-medium"
              disabled={isLoading}
              maxLength={10}
            />
          </div>
          <button
            type="submit"
            disabled={!ticker.trim() || isLoading}
            className="px-8 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Researching...</span>
              </>
            ) : (
              <>
                <Sparkles className="h-5 w-5" />
                <span>Research</span>
              </>
            )}
          </button>
        </div>

        {/* Quick Ticker Buttons */}
        <div className="mt-4 flex flex-wrap gap-2">
          <span className="text-sm text-gray-500 mr-2 self-center">Quick:</span>
          {quickTickers.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTicker(t)}
              disabled={isLoading}
              className="px-3 py-1.5 text-sm font-medium text-gray-600 bg-gray-100 rounded-full hover:bg-gray-200 hover:text-gray-800 disabled:opacity-50 transition-colors"
            >
              {t}
            </button>
          ))}
        </div>

        {/* Settings Toggle */}
        <div className="mt-4 border-t border-gray-100 pt-4">
          <button
            type="button"
            onClick={() => setShowSettings(!showSettings)}
            className="flex items-center gap-2 text-sm text-gray-600 hover:text-gray-800"
          >
            <Settings className="h-4 w-4" />
            <span>Advanced Settings</span>
            {showSettings ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>

          {showSettings && (
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Reset Memory Toggle */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2">
                  <RefreshCw className="h-4 w-4 text-gray-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Reset Memory
                    </p>
                    <p className="text-xs text-gray-500">
                      Clear context from previous research
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setResetMemory(!resetMemory)}
                  className={`relative w-12 h-6 rounded-full transition-colors ${
                    resetMemory ? 'bg-primary-600' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
                      resetMemory ? 'translate-x-6' : ''
                    }`}
                  />
                </button>
              </div>

              {/* Model Provider Selection */}
              <div className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Cpu className="h-4 w-4 text-gray-500" />
                  <p className="text-sm font-medium text-gray-700">
                    Model Provider
                  </p>
                </div>
                <div className="flex gap-2">
                  {MODEL_PROVIDERS.map((provider) => (
                    <button
                      key={provider.id}
                      type="button"
                      onClick={() =>
                        !provider.disabled && setModelProvider(provider.id)
                      }
                      disabled={provider.disabled}
                      className={`flex-1 px-3 py-2 text-sm rounded-lg border transition-all ${
                        modelProvider === provider.id
                          ? 'border-primary-500 bg-primary-50 text-primary-700'
                          : provider.disabled
                          ? 'border-gray-200 bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                    >
                      <div className="font-medium">{provider.name}</div>
                      <div className="text-xs opacity-75">
                        {provider.description}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </form>
    </div>
  )
}

function AgentProgress({ isLoading, logs }) {
  const agents = [
    {
      name: 'Manager',
      icon: Brain,
      description: 'Coordinating research workflow',
    },
    {
      name: 'Researcher',
      icon: Search,
      description: 'Gathering news & sentiment',
    },
    {
      name: 'Analyst',
      icon: TrendingUp,
      description: 'Analyzing financial metrics',
    },
    {
      name: 'Reporter',
      icon: FileText,
      description: 'Generating final report',
    },
  ]

  if (!isLoading && logs.length === 0) return null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-4">
        <Bot className="h-5 w-5 text-primary-600" />
        <h2 className="text-lg font-semibold text-gray-800">Agent Activity</h2>
      </div>

      {/* Agent Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        {agents.map((agent, idx) => {
          const Icon = agent.icon
          const isActive = isLoading && idx <= Math.floor(Math.random() * 4)

          return (
            <div
              key={agent.name}
              className={`p-3 rounded-lg border transition-all ${
                isActive
                  ? 'border-primary-300 bg-primary-50'
                  : 'border-gray-200 bg-gray-50'
              }`}
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon
                  className={`h-4 w-4 ${
                    isActive ? 'text-primary-600' : 'text-gray-400'
                  }`}
                />
                <span
                  className={`text-sm font-medium ${
                    isActive ? 'text-primary-700' : 'text-gray-600'
                  }`}
                >
                  {agent.name}
                </span>
                {isActive && (
                  <div className="ml-auto flex space-x-1">
                    <span className="loading-dot w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                    <span className="loading-dot w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                    <span className="loading-dot w-1.5 h-1.5 bg-primary-500 rounded-full"></span>
                  </div>
                )}
              </div>
              <p className="text-xs text-gray-500">{agent.description}</p>
            </div>
          )
        })}
      </div>

      {/* Log Output */}
      <div className="bg-gray-900 rounded-lg p-4 font-mono text-sm max-h-32 overflow-y-auto">
        {logs.map((log, idx) => (
          <div key={idx} className="text-gray-300">
            <span className="text-gray-500">[{idx + 1}]</span> {log}
          </div>
        ))}
        {isLoading && (
          <div className="text-primary-400 flex items-center gap-2">
            <Loader2 className="h-3 w-3 animate-spin" />
            <span>Processing...</span>
          </div>
        )}
      </div>
    </div>
  )
}

function ReportViewer({ report, duration, onClear }) {
  const handleDownload = () => {
    const blob = new Blob([report], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'finresearch_report.md'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (!report) return null

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-50 to-emerald-50 border-b border-green-100 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-green-100 p-2 rounded-lg">
              <CheckCircle2 className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">
                Research Report
              </h2>
              {duration && (
                <div className="flex items-center gap-1 text-sm text-gray-500">
                  <Clock className="h-3 w-3" />
                  <span>Generated in {duration.toFixed(1)}s</span>
                </div>
              )}
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleDownload}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Download className="h-4 w-4" />
              Download
            </button>
            <button
              onClick={onClear}
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              New Research
            </button>
          </div>
        </div>
      </div>

      {/* Report Content */}
      <div className="p-6 max-h-[600px] overflow-y-auto">
        <div className="markdown-content">
          <ReactMarkdown>{report}</ReactMarkdown>
        </div>
      </div>
    </div>
  )
}

function ErrorDisplay({ error, onRetry }) {
  if (!error) return null

  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6">
      <div className="flex items-start gap-3">
        <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
        <div className="flex-1">
          <h3 className="text-red-800 font-semibold">Research Failed</h3>
          <p className="text-red-700 mt-1">{error}</p>
          <button
            onClick={onRetry}
            className="mt-3 px-4 py-2 text-sm font-medium text-red-700 bg-red-100 rounded-lg hover:bg-red-200 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    </div>
  )
}

function Features() {
  const features = [
    {
      icon: Brain,
      title: 'Manager Agent',
      description:
        'GPT-4o-mini powered coordinator that orchestrates the research workflow',
    },
    {
      icon: Search,
      title: 'Research Agent',
      description:
        'Gathers news, analyzes sentiment, and identifies key developments',
    },
    {
      icon: TrendingUp,
      title: 'Analysis Agent',
      description:
        'Processes financial metrics, valuations, and market data',
    },
    {
      icon: FileText,
      title: 'Reporter Agent',
      description:
        'Synthesizes findings into comprehensive markdown reports',
    },
  ]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4">
        How It Works
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {features.map((feature, idx) => {
          const Icon = feature.icon
          return (
            <div key={feature.title} className="text-center p-4">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-100 text-primary-600 rounded-xl mb-3">
                <Icon className="h-6 w-6" />
              </div>
              <div className="flex items-center justify-center gap-2 mb-1">
                <span className="text-xs font-medium text-primary-600 bg-primary-100 px-2 py-0.5 rounded-full">
                  {idx + 1}
                </span>
                <h3 className="font-medium text-gray-800">{feature.title}</h3>
              </div>
              <p className="text-sm text-gray-500">{feature.description}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

// =============================================================================
// Main App Component
// =============================================================================

function App() {
  const {
    isLoading,
    report,
    logs,
    error,
    duration,
    runResearch,
    clearResults,
  } = useResearch()

  const handleSearch = (ticker, options) => {
    runResearch(ticker, options)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        {/* Search Section */}
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Error Display */}
        <ErrorDisplay error={error} onRetry={clearResults} />

        {/* Agent Progress */}
        <AgentProgress isLoading={isLoading} logs={logs} />

        {/* Report Viewer */}
        <ReportViewer
          report={report}
          duration={duration}
          onClear={clearResults}
        />

        {/* Features Section (show when no report) */}
        {!report && !isLoading && !error && <Features />}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <p>
              Built with CrewAI, FastAPI, and React
            </p>
            <p>FinResearch AI v1.0.0</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
