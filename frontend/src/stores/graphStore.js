import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/api/client'

export const useGraphStore = defineStore('graph', () => {
  // State
  const currentDocId = ref(null)
  const nodes = ref([])
  const edges = ref([])
  const docFrags = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const isDirty = ref(false)
  
  // Upload state
  const uploadProgress = ref(0)
  const extractionStatus = ref(null)
  const currentJobId = ref(null)
  
  // Getters
  const nodeCount = computed(() => nodes.value.length)
  const edgeCount = computed(() => edges.value.length)
  const hasData = computed(() => nodes.value.length > 0)
  
  // Actions
  async function uploadDocument(file) {
    try {
      isLoading.value = true
      error.value = null
      
      const result = await api.uploadDocument(file)
      currentDocId.value = result.doc_id
      
      console.log('Document uploaded:', result)
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  async function startExtraction() {
    if (!currentDocId.value) {
      throw new Error('No document uploaded')
    }
    
    try {
      isLoading.value = true
      const result = await api.startExtraction(currentDocId.value)
      currentJobId.value = result.job_id
      extractionStatus.value = result.status
      
      // Poll for status
      pollExtractionStatus()
      
      return result
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  async function pollExtractionStatus() {
    if (!currentJobId.value) return
    
    const poll = async () => {
      try {
        const status = await api.getJobStatus(currentJobId.value)
        extractionStatus.value = status.status
        
        if (status.status === 'done') {
          // Load graph data
          await loadGraph(currentDocId.value)
        } else if (status.status === 'error') {
          error.value = status.message
        } else {
          // Continue polling
          setTimeout(poll, 2000)
        }
      } catch (err) {
        console.error('Failed to poll status:', err)
        error.value = err.message
      }
    }
    
    poll()
  }
  
  async function loadGraph(docId) {
    try {
      isLoading.value = true
      error.value = null
      
      const data = await api.getGraph(docId)
      
      // Convert to VueFlow format
      nodes.value = data.nodes.map(node => ({
        id: node.id,
        type: node.type.toLowerCase(),
        position: { x: Math.random() * 500, y: Math.random() * 500 },
        data: {
          label: node.label,
          ...node.props
        }
      }))
      
      edges.value = data.edges.map(edge => ({
        id: edge.id,
        source: edge.from,
        target: edge.to,
        type: edge.type.toLowerCase(),
        animated: edge.type === 'EMITS',
        label: edge.type
      }))
      
      docFrags.value = data.doc_frags || []
      currentDocId.value = docId
      isDirty.value = false
      
      console.log('Graph loaded:', { nodes: nodes.value.length, edges: edges.value.length })
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  function updateNode(nodeId, updates) {
    const index = nodes.value.findIndex(n => n.id === nodeId)
    if (index !== -1) {
      nodes.value[index] = { ...nodes.value[index], ...updates }
      isDirty.value = true
    }
  }
  
  function addNode(node) {
    nodes.value.push(node)
    isDirty.value = true
  }
  
  function removeNode(nodeId) {
    nodes.value = nodes.value.filter(n => n.id !== nodeId)
    // Also remove connected edges
    edges.value = edges.value.filter(e => e.source !== nodeId && e.target !== nodeId)
    isDirty.value = true
  }
  
  function addEdge(edge) {
    edges.value.push(edge)
    isDirty.value = true
  }
  
  function removeEdge(edgeId) {
    edges.value = edges.value.filter(e => e.id !== edgeId)
    isDirty.value = true
  }
  
  async function saveGraph() {
    try {
      isLoading.value = true
      
      // Convert back to API format
      const apiNodes = nodes.value.map(node => ({
        id: node.id,
        type: node.type.charAt(0).toUpperCase() + node.type.slice(1),
        label: node.data.label,
        props: node.data
      }))
      
      const apiEdges = edges.value.map(edge => ({
        id: edge.id,
        type: edge.type.toUpperCase(),
        from: edge.source,
        to: edge.target,
        props: {}
      }))
      
      await Promise.all([
        api.saveNodes(apiNodes),
        api.saveEdges(apiEdges)
      ])
      
      isDirty.value = false
      console.log('Graph saved successfully')
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  function reset() {
    currentDocId.value = null
    nodes.value = []
    edges.value = []
    docFrags.value = []
    error.value = null
    isDirty.value = false
    uploadProgress.value = 0
    extractionStatus.value = null
    currentJobId.value = null
  }
  
  return {
    // State
    currentDocId,
    nodes,
    edges,
    docFrags,
    isLoading,
    error,
    isDirty,
    uploadProgress,
    extractionStatus,
    
    // Getters
    nodeCount,
    edgeCount,
    hasData,
    
    // Actions
    uploadDocument,
    startExtraction,
    loadGraph,
    updateNode,
    addNode,
    removeNode,
    addEdge,
    removeEdge,
    saveGraph,
    reset
  }
})



