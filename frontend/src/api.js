const API_BASE = 'http://localhost:8000'

export const api = {
  async createAgent(description) {
    const res = await fetch(`${API_BASE}/api/agents/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ description })
    })
    if (!res.ok) {
      const error = await res.text()
      throw new Error(`Failed to create agent: ${error}`)
    }
    return res.json()
  },

  async getAgent(agentId) {
    const res = await fetch(`${API_BASE}/api/agents/${agentId}`)
    if (!res.ok) throw new Error('Failed to get agent')
    return res.json()
  }
}
