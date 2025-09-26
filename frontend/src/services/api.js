import axios from 'axios';

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentService = {
  // Upload a document
  uploadDocument: async (file, tag, authHeaders = {}) => {
    console.log('DEBUG: uploadDocument called with:', { file, tag, authHeaders });
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tag', tag);
    
    // Create headers without Content-Type for FormData uploads
    const headers = { ...authHeaders };
    // Remove any Content-Type to let browser set multipart boundary
    delete headers['Content-Type'];
    
    console.log('DEBUG: Request headers:', headers);
    console.log('DEBUG: FormData entries:', [...formData.entries()]);
    
    // Make request directly with axios instead of using the api instance
    // to avoid any default header conflicts
    const response = await axios.post(`${API_BASE_URL}/documents/upload`, formData, { 
      headers,
      timeout: 30000 // 30 second timeout
    });
    return response.data;
  },

  // Get all documents
  getAllDocuments: async (authHeaders = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };
    const response = await api.get('/documents/', { headers });
    return response.data;
  },

  // Get documents by tag
  getDocumentsByTag: async (tag, authHeaders = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };
    const response = await api.get(`/documents/tag/${encodeURIComponent(tag)}`, { headers });
    return response.data;
  },

  // Get document by ID
  getDocumentById: async (id, authHeaders = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };
    const response = await api.get(`/documents/${id}`, { headers });
    return response.data;
  },

  // Update document
  updateDocument: async (id, data, authHeaders = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };
    const response = await api.put(`/documents/${id}`, data, { headers });
    return response.data;
  },

  // Delete document
  deleteDocument: async (id, authHeaders = {}) => {
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders,
    };
    const response = await api.delete(`/documents/${id}`, { headers });
    return response.data;
  },
};

export default api;