import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
client.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
client.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default client

// API methods
export const api = {
  // Document upload
  async uploadDocument(file) {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/docs/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // Start extraction
  async startExtraction(docId) {
    return client.post('/extract/run', { doc_id: docId })
  },

  // Get job status
  async getJobStatus(jobId) {
    return client.get('/extract/status', { params: { job_id: jobId } })
  },

  // Get graph data
  async getGraph(docId) {
    return client.get('/graph', { params: { doc_id: docId } })
  },

  // Create/update nodes
  async saveNodes(nodes) {
    return client.post('/graph/nodes', { nodes })
  },

  // Create/update edges
  async saveEdges(edges) {
    return client.post('/graph/edges', { edges })
  },

  // Delete node
  async deleteNode(nodeId) {
    return client.delete(`/graph/nodes/${nodeId}`)
  },

  // Delete edge
  async deleteEdge(edgeId) {
    return client.delete(`/graph/edges/${edgeId}`)
  },

  // Get MS candidates
  async getMSCandidates(docId) {
    return client.get('/graph/recommend/ms-candidates', { params: { doc_id: docId } })
  }
}



