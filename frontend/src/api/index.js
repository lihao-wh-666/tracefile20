import axios from 'axios'

const getCsrfToken = () => {
  const name = 'csrftoken'
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        return decodeURIComponent(cookie.substring(name.length + 1))
      }
    }
  }
  return null
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  withCredentials: true
})

api.interceptors.request.use(
  config => {
    const csrfToken = getCsrfToken()
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error)
    if (error.response) {
      if (error.response.status === 401) {
        localStorage.removeItem('user')
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
      if (error.response.status === 403) {
        const detail = error.response.data?.detail || ''
        if (detail.includes('锁定') || detail.includes('登录失败')) {
          return Promise.reject(error)
        }
        if (detail.includes('认证') || detail.includes('未提供') || detail.includes('权限')) {
          localStorage.removeItem('user')
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          return Promise.reject(error)
        }
      }
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  getCsrfToken: () => api.get('/auth/csrf/'),
  login: (data) => api.post('/auth/login/', data),
  logout: () => api.post('/auth/logout/'),
  getUserInfo: () => api.get('/auth/user/'),
  updateUserInfo: (data) => api.put('/auth/user/update/', data),
  changePassword: (data) => api.post('/auth/password/change/', data)
}

export const userApi = {
  getProfile: () => api.get('/user/profile/'),
  updateProfile: (data) => api.put('/user/profile/', data),
  getPreferences: () => api.get('/user/preferences/'),
  updatePreferences: (data) => api.put('/user/preferences/', data)
}

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
  delete: (id) => api.delete(`/archives/${id}/`),
  submitForReview: (id) => api.post(`/archives/${id}/submit_for_review/`),
  approve: (id, data) => api.post(`/archives/${id}/approve/`, data),
  reject: (id, data) => api.post(`/archives/${id}/reject/`, data),
  export: (data) => api.post('/archives/export/', data, { responseType: 'blob' }),
  getVersions: (id) => api.get(`/archives/${id}/versions/`),
  getVersionDetail: (id, versionId) => api.get(`/archives/${id}/versions/${versionId}/`),
  rollback: (id, data) => api.post(`/archives/${id}/rollback/`, data),
  getRejectRecords: (id) => api.get(`/archives/${id}/reject_records/`)
}

export const archiveVersionApi = {
  getAll: (params) => api.get('/archive-versions/', { params }),
  getById: (id) => api.get(`/archive-versions/${id}/`)
}

export const rejectRecordApi = {
  getAll: (params) => api.get('/reject-records/', { params }),
  getById: (id) => api.get(`/reject-records/${id}/`)
}

export const archiveLogApi = {
  getAll: (params) => api.get('/archive-logs/', { params }),
  getById: (id) => api.get(`/archive-logs/${id}/`)
}

export const todoApi = {
  getAll: (params) => api.get('/todos/', { params }),
  getById: (id) => api.get(`/todos/${id}/`),
  create: (data) => api.post('/todos/', data),
  update: (id, data) => api.put(`/todos/${id}/`, data),
  delete: (id) => api.delete(`/todos/${id}/`),
  getUnreadCount: () => api.get('/todos/unread_count/'),
  markAllRead: () => api.post('/todos/mark_all_read/'),
  toggleStatus: (id) => api.post(`/todos/${id}/toggle_status/`)
}

export default api
