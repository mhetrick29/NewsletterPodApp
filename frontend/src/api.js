/**
 * API client for Newsletter Podcast Agent backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 300000, // 5 minute timeout for AI operations
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

  // Get daily summary grouped by category
  getSummary: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/summary', { params });
    return response.data;
  },

  // Get AI-powered summary for a single newsletter
  getAiSummary: async (newsletterId) => {
    const response = await api.get(`/api/newsletters/${newsletterId}/ai-summary`);
    return response.data;
  },

  // Get AI-powered summaries for all newsletters on a date
  getAiDailySummary: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/ai-summary', { params });
    return response.data;
  },

  // Get podcast-style daily briefing
  getDailyBriefing: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/daily-briefing', { params });
    return response.data;
  },
};

export default api;
