import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const categoryApi = {
  getAll: () => api.get('/categories/'),
  getTree: () => api.get('/categories/tree/'),
  getSimple: () => api.get('/categories/simple/'),
  getById: (id) => api.get(`/categories/${id}/`),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}/`, data),
  delete: (id) => api.delete(`/categories/${id}/`)
}

export const archiveApi = {
  getAll: (params) => api.get('/archives/', { params }),
  getById: (id) => api.get(`/archives/${id}/`),
  create: (data) => api.post('/archives/', data),
  update: (id, data) => api.put(`/archives/${id}/`, data),
  delete: (id) => api.delete(`/archives/${id}/`)
}

export default api
