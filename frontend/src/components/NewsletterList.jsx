import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { newsletterApi } from '../api';
import FilterBar from './FilterBar';
import './NewsletterList.css';

function NewsletterList() {
  const navigate = useNavigate();
  const [newsletters, setNewsletters] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    category: '',
    startDate: '',
    endDate: '',
  });

  useEffect(() => {
    loadNewsletters();
    loadCategories();
  }, [filters]);

  const loadNewsletters = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {};
      if (filters.category) params.category = filters.category;
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      
      const data = await newsletterApi.getNewsletters(params);
      setNewsletters(data);
    } catch (err) {
      setError('Failed to load newsletters. Make sure the backend is running.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      const data = await newsletterApi.getCategories();
      setCategories(data);
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleNewsletterClick = (newsletter) => {
    navigate(`/newsletter/${newsletter.id}`);
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'product_ai': 'Product & AI',
      'health_fitness': 'Health & Fitness',
      'finance': 'Finance',
      'sahil_bloom': 'Sahil Bloom',
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category) => {
    const colors = {
      'product_ai': '#3498db',
      'health_fitness': '#2ecc71',
      'finance': '#f39c12',
      'sahil_bloom': '#9b59b6',
    };
    return colors[category] || '#95a5a6';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <span>Loading newsletters...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <h3>Error</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="newsletter-list-container">
      <FilterBar
        categories={categories}
        filters={filters}
        onFilterChange={handleFilterChange}
      />

      {newsletters.length === 0 ? (
        <div className="empty-state">
          <h2>No Newsletters Found</h2>
          <p>Click "Extract Newsletters" to fetch newsletters from Gmail</p>
        </div>
      ) : (
        <>
          <div className="results-count">
            Showing {newsletters.length} newsletter{newsletters.length !== 1 ? 's' : ''}
          </div>
          
          <div className="newsletter-grid">
            {newsletters.map((newsletter) => (
              <div
                key={newsletter.id}
                className="newsletter-card"
                onClick={() => handleNewsletterClick(newsletter)}
              >
                <div className="newsletter-header">
                  <span
                    className="category-badge"
                    style={{ backgroundColor: getCategoryColor(newsletter.category) }}
                  >
                    {getCategoryLabel(newsletter.category)}
                  </span>
                  <span className="platform-badge">{newsletter.platform}</span>
                </div>
                
                <h3 className="newsletter-subject">{newsletter.subject}</h3>
                
                <div className="newsletter-meta">
                  <div className="sender">
                    <strong>{newsletter.sender_name}</strong>
                  </div>
                  <div className="date">{formatDate(newsletter.date)}</div>
                </div>
                
                {newsletter.needs_review && (
                  <div className="review-badge">⚠️ Needs Review</div>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

export default NewsletterList;
