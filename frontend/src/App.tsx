import React from 'react'

function App() {
  return (
    <div className="app-container">
      <header>
        <h1>AI Icarus V2 Beta</h1>
        <p>Log Analytics Query Assistant with Microsoft Agent Framework</p>
      </header>
      <main>
        <div className="status-message">
          <h2>Coming Soon</h2>
          <p>Frontend implementation in progress...</p>
          <p>Backend API: {import.meta.env.VITE_API_URL || 'Not configured'}</p>
          <p>Azure Cloud: {import.meta.env.VITE_AZURE_CLOUD || 'AzureUSGovernment'}</p>
        </div>
      </main>
      <footer>
        <p>Powered by Microsoft Agent Framework</p>
      </footer>
    </div>
  )
}

export default App