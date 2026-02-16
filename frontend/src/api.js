/**
 * API client for Newsletter Podcast Agent backend
 */
import axios from 'axios';

const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' },
  timeout: 300000, // 5 minute timeout for AI operations
});

export const newsletterApi = {
  /**
   * Fetch newsletters from Gmail for a specific date.
   * @param {string} targetDate - YYYY-MM-DD (optional, defaults to today on server)
   */
  extractNewsletters: async (targetDate = null) => {
    const body = {};
    if (targetDate) body.target_date = targetDate;
    const response = await api.post('/api/extract', body);
    return response.data;
  },

  /**
   * Get list of newsletters already stored for a date.
   * @param {string} date - YYYY-MM-DD (optional)
   */
  getNewsletters: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/newsletters', { params });
    return response.data;
  },

  /**
   * Download a PDF summary for a date (triggers browser download).
   * @param {string} date - YYYY-MM-DD (optional)
   */
  downloadSummaryPdf: async (date = null) => {
    const params = date ? { date } : {};
    const response = await api.get('/api/summary-pdf', {
      params,
      responseType: 'blob',
    });
    const url = window.URL.createObjectURL(
      new Blob([response.data], { type: 'application/pdf' })
    );
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `newsletter-summary-${date || 'today'}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  },
};

export default api;
