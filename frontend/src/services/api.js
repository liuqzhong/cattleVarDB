/**
 * ============================================
 * API Service
 * ============================================
 */

import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    const message = error.response?.data?.message || error.message || '请求失败'
    return Promise.reject(new Error(message))
  }
)

/**
 * SNP API endpoints
 */
export const snpApi = {
  /**
   * Get SNP list with pagination
   * @param {Object} params - Query parameters
   * @param {number} params.page - Page number (default: 1)
   * @param {number} params.page_size - Items per page (default: 20)
   * @param {string} params.sort_by - Sort field (default: 'id')
   * @param {string} params.sort_order - Sort direction: 'asc' or 'desc' (default: 'asc')
   * @param {number} params.top_n - Top N effect values to include (default: 10)
   */
  getList(params) {
    return apiClient.get('/snps', { params })
  },

  /**
   * Search SNPs by query
   * @param {string} query - Search query (chr:position or rsID)
   * @param {Object} params - Additional parameters
   * @param {number} params.page - Page number
   * @param {number} params.page_size - Items per page
   * @param {number} params.top_n - Top N effect values to include
   */
  search(query, params = {}) {
    return apiClient.get('/snps/search', {
      params: { query, ...params }
    })
  },

  /**
   * Get SNP detail by ID
   * @param {number} id - SNP ID
   */
  getDetail(id) {
    return apiClient.get(`/snps/${id}`)
  }
}

/**
 * Target API endpoints
 */
export const targetApi = {
  /**
   * Get target list
   * @param {Object} params - Query parameters
   * @param {number} params.skip - Skip records
   * @param {number} params.limit - Limit records
   */
  getList(params = {}) {
    return apiClient.get('/targets', { params })
  }
}

/**
 * Genomics API endpoints
 */
export const genomicsApi = {
  /**
   * Get genomic region data
   * @param {string} chrom - Chromosome
   * @param {number} start - Start position
   * @param {number} end - End position
   */
  getRegion(chrom, start, end) {
    return apiClient.get(`/genomics/region/${chrom}`, {
      params: { start, end }
    })
  }
}

/**
 * Statistics API
 */
export const statsApi = {
  /**
   * Get database statistics
   */
  getStats() {
    return apiClient.get('/stats')
  }
}

/**
 * Health check
 */
export const healthApi = {
  check() {
    return apiClient.get('/health')
  }
}

export default apiClient
