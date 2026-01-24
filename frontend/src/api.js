/**
 * API client for Newsletter Podcast Agent backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const newsletterApi = {
  // Get list of newsletters with optional filtering
  getNewsletters: async (params = {}) => {
    const response = await api.get('/api/newsletters', { params });
    return response.data;
  },

  // Get single newsletter by ID
  getNewsletter: async (id) => {
    const response = await api.get(`/api/newsletters/${id}`);
    return response.data;
  },

  // Get all categories with counts
  getCategories: async () => {
    const response = await api.get('/api/categories');
    return response.data;
  },

  // Trigger newsletter extraction from Gmail
  extractNewsletters: async (daysBack = 1, maxResults = 100) => {
    const response = await api.post('/api/extract', {
      days_back: daysBack,
      max_results: maxResults,
    });
    return response.data;
  },

  // Get overall statistics
  getStats: async () => {
    const response = await api.get('/api/stats');
    return response.data;
  },
};

export default api;
