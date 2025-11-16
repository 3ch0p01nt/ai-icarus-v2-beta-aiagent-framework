import { useState, useEffect } from 'react'

interface HelloResponse {
  status: string
  message: string
  cloud?: string
  deployment?: string
  test_prompt?: string
  ai_response?: string
  note?: string
  error?: string
  usage?: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

function App() {
  const [helloData, setHelloData] = useState<HelloResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    // Fetch the hello world AI test when component mounts
    const fetchHello = async () => {
      try {
        setLoading(true)
        const response = await fetch(`${apiUrl}/api/hello`)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data: HelloResponse = await response.json()
        setHelloData(data)
        setError(null)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch')
      } finally {
        setLoading(false)
      }
    }

    fetchHello()
  }, [apiUrl])

  const handleRefresh = () => {
    setLoading(true)
    setError(null)
    window.location.reload()
  }

  return (
    <div className="app-container">
      <header>
        <h1>AI Icarus V2 Beta</h1>
        <p>Log Analytics Query Assistant with Microsoft Agent Framework</p>
      </header>
      <main>
        <div className="status-message">
          {loading ? (
            <>
              <h2>Loading...</h2>
              <p>Calling Azure OpenAI...</p>
            </>
          ) : error ? (
            <>
              <h2>Error</h2>
              <p style={{ color: '#ff6b6b' }}>{error}</p>
              <button onClick={handleRefresh} style={{ marginTop: '1rem', padding: '0.5rem 1rem', cursor: 'pointer' }}>
                Retry
              </button>
            </>
          ) : helloData ? (
            <>
              <h2>{helloData.message}</h2>

              {helloData.cloud && (
                <p><strong>Cloud:</strong> {helloData.cloud}</p>
              )}

              {helloData.deployment && (
                <p><strong>Deployment:</strong> {helloData.deployment}</p>
              )}

              <div style={{
                marginTop: '2rem',
                padding: '1.5rem',
                background: '#f0f4f8',
                borderRadius: '8px',
                borderLeft: '4px solid #3b82f6'
              }}>
                <h3 style={{ marginTop: 0 }}>AI Test Result</h3>

                {helloData.test_prompt && (
                  <div style={{ marginBottom: '1rem' }}>
                    <strong>Test Prompt:</strong>
                    <p style={{
                      fontStyle: 'italic',
                      color: '#555',
                      marginTop: '0.5rem'
                    }}>
                      "{helloData.test_prompt}"
                    </p>
                  </div>
                )}

                {helloData.ai_response ? (
                  <div>
                    <strong>AI Response:</strong>
                    <p style={{
                      background: 'white',
                      padding: '1rem',
                      borderRadius: '4px',
                      marginTop: '0.5rem',
                      whiteSpace: 'pre-wrap',
                      lineHeight: '1.6'
                    }}>
                      {helloData.ai_response}
                    </p>

                    {helloData.usage && (
                      <div style={{
                        marginTop: '1rem',
                        fontSize: '0.875rem',
                        color: '#666'
                      }}>
                        <strong>Token Usage:</strong> {helloData.usage.total_tokens} total
                        ({helloData.usage.prompt_tokens} prompt + {helloData.usage.completion_tokens} completion)
                      </div>
                    )}
                  </div>
                ) : helloData.note ? (
                  <p style={{ color: '#f59e0b' }}>{helloData.note}</p>
                ) : helloData.error ? (
                  <p style={{ color: '#ef4444' }}><strong>Error:</strong> {helloData.error}</p>
                ) : (
                  <p>No AI response available</p>
                )}
              </div>

              <div style={{ marginTop: '2rem', fontSize: '0.875rem', color: '#666' }}>
                <p><strong>Backend API:</strong> {apiUrl}</p>
                <p><strong>Azure Cloud:</strong> {import.meta.env.VITE_AZURE_CLOUD || 'AzureUSGovernment'}</p>
                <p><strong>Status:</strong> <span style={{ color: helloData.status === 'success' ? '#10b981' : '#f59e0b' }}>
                  {helloData.status}
                </span></p>
              </div>

              <button
                onClick={handleRefresh}
                style={{
                  marginTop: '1.5rem',
                  padding: '0.75rem 1.5rem',
                  background: '#3b82f6',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  fontWeight: '500'
                }}
              >
                Get New AI Response
              </button>
            </>
          ) : null}
        </div>
      </main>
      <footer>
        <p>Powered by Microsoft Agent Framework</p>
      </footer>
    </div>
  )
}

export default App